from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import func, between, extract, column, desc, asc, select
from twisted.internet import defer


class Query(defer.Deferred):

    """ An incomplete query """

    def __init__(self, model, query=None):
        defer.Deferred.__init__(self)
        self.model = model
        self.query = query
        self.offset = None
        self.limit = None
        self._order_by = None
        self.deferred = None

    def _clone(self):
        q = Query(self.model)
        return q

    def _filter(self, **terms):
        filters = []
        for k, v in terms.items():
            if not "__" in k:
                comparison = "exact"
            else:
                k, comparison = k.split("__")

            try:
                column = getattr(self.model.__table__.c, k)
            except AttributeError:
                raise KeyError("Invalid key '%s'" % k)

            lookups = {
                "exact": lambda c, v: c == v,
                "day": lambda c, v: extract('day', c) == v,
                "month": lambda c, v: extract('month', c) == v,
                "year": lambda c, v: extract('year', c) == v,
                "week_date": lambda c, v: extract('dow', c) == v,
                "in": lambda c, v: c.in_(v),
                "contains": lambda c, v: c.contains(v),
                "icontains": lambda c, v: c.ilike("%" + v + "%"),
                "startswith": lambda c, v: c.startswith(v),
                "istartswith": lambda c, v: c.ilike(v + "%"),
                "endswith": lambda c, v: c.endswith(v),
                "iendswith": lambda c, v: c.ilike("%" + v),
                "range": lambda c, v: between(c, v[0], v[1]),
                "isnull": lambda c, v: c == None if v else c != None,
                }

            if not comparison in lookups:
                raise KeyError("Invalid comparison type %s" % comparison)

            filters.append(lookups[comparison](column, v))

        return and_(*filters)

    def filter(self, **terms):
        q = self._clone()
        query = self._filter(**terms)
        if self.query is not None:
            query = and_(self.query, query)
        q.query = query
        return q

    def exclude(self, **terms):
        q = self._clone()
        query = not_(self._filter(**terms))
        if self.query is not None:
            query = and_(self.query, query)
        q.query = query
        return q

    def order_by(self, *terms):
        q = self._clone()

        columns = []
        for t in terms:
            order = asc
            if t[0] in "+-":
                order = desc if t[0] == '-' else asc
                t = t[1:]
            c = order(column(t))
            columns.append(c)

        q._order_by = columns

        return q

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            q = self._clone()
            q.offset = idx.start
            q.limit = idx.stop
            return q
        raise IndexError("Invalid splice")

    def update(self, **kwargs):
        """ Updates all rows that match the query """
        expr = self.model.__table__.update().where(self.query).values(**kwargs)
        return self._runquery(expr)

    def delete(self):
        """ Deletes all rows that match the query """
        expr = self.model.__table__.delete().where(self.query)
        return self._runquery(expr)

    def exists(self):
        expr = exists().where(self.query)
        return self._runquery(expr)

    @defer.inlineCallbacks
    def count(self):
        expr = select([func.count(self.model.__table__.c.id)])
        if self.query is not None:
            expr = expr.where(self.query)
        results = yield self._runquery(expr)
        defer.returnValue(results[0][0])

    @defer.inlineCallbacks
    def get(self, **kwargs):
        results = yield self.filter(**kwargs)._select()
        if len(results) == 0:
            raise self.model.DoesNotExist()
        elif len(results) > 1:
            raise self.model.MultipleObjectsReturned()
        else:
            defer.returnValue(results[0])

    def _runquery(self, expression):
        return self.model.connection.run(expression)

    @defer.inlineCallbacks
    def _select(self):
        columns = [c.name for c in self.model.__table__.columns]
        expr = select([self.model.__table__])
        if self.query is not None:
            expr = expr.where(self.query)
        if self.limit:
            expr = expr.limit(self.limit)
        if self.offset:
            expr = expr.offset(self.offset)
        if self._order_by:
            expr = expr.order_by(*self._order_by)
        results = yield self._runquery(expr)
        final = []
        for result in results:
            constructargs = {}
            for c, v in zip(self.model.__table__.columns, result):
                p = c.type._cached_result_processor(self.model.connection.dialect, c.type)
                constructargs[c.name] = p(v) if p else v
            r = self.model()
            r._construct(**constructargs)
            final.append(r)
        defer.returnValue(final)

    def addCallbacks(self, *args, **kwargs):
        if not self.deferred:
            self.deferred = self._select()
            self.deferred.chainDeferred(self)
        return defer.Deferred.addCallbacks(self, *args, **kwargs)


