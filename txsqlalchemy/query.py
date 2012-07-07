from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import func, between, extract, column, desc, asc, select
from twisted.internet import defer


class Query(object):

    """ An incomplete query """

    def __init__(self, model, query=None):
        self.model = model
        self.query = query

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
           
            if comparison == "exact":
                filters.append(column == v)
            elif comparison == "day":
                filters.append(extract('day', column) == v)
            elif comparison == "month":
                filters.append(extract('month', column) == v)
            elif comparison == "year":
                filters.append(extract('year', column) == v)
            elif comparison == "week_date":
                filters.append(extract('dow', column) == v)
            elif comparison == "in":
                filters.append(column.in_(v))
            elif comparison == "contains":
                filters.append(column.contains(v))
            elif comparison == "icontains":
                filters.append(column.ilike("%" + v + "%"))
            elif comparison == "startswith":
                filters.append(column.startswith(v))
            elif comparison == "istartswith":
                filters.append(column.ilike(v + "%"))
            elif comparison == "endswith":
                filters.append(column.endswith(v))
            elif comparison == "iendswith":
                filters.append(column.ilike("%" + v))
            elif comparison == "range":
                filters.append(between(column, v[0], v[1]))
            elif comparison == "isnull":
                if v:
                    filters.append(column == None)
                else:
                    filters.append(column != None)
            else:
                raise KeyError("Invalid comparison type %s" % comparison)

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

    def order_by(self, terms):
        q = self._clone()

        columns = []
        for t in terms.split(" "):
            desc = False
            if t[0] in "+-":
                order = desc if t[0] == '-' else asc
                t = t[1:]
            c = order(column(t))
            columns.append(c)

        q.query = self.query.order_by(*c)

        return q

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
    def select(self):
        columns = [c.name for c in self.model.__table__.columns]
        expr = select([self.model.__table__])
        if self.query is not None:
            expr = expr.where(self.query)
        results = yield self._runquery(expr)
        final = []
        for result in results:
            r = self.model(**dict(zip(columns, result)))
            r._is_new_record = False
            final.append(r)
        defer.returnValue(final)

    def _runquery(self, expression):
        return self.model.connection.run(expression)

