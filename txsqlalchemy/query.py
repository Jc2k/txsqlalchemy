from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import between, extract, column, desc, asc, select
from twisted.internet import defer


class Query(object):

    """ An incomplete query """

    def __init__(self, model, query=None):
        self.model = model
        self.query = query

    def _clone(self):
        q = Query(self.model)
        return q

    def filter(self, **terms):
        q = self._clone()

        filters = []
        for k, v in terms.items():
            if not "__" in k:
                comparison = "exact"
            else:
                k, comparison = k.split("__")

            try:
                column = getattr(self.model.c, k)
            except AttributeError:
                raise KeyError("Invalid key '%s'" % k)
           
            if comparison == "exact":
                filters.append(column == v)
            elif comparison == "day":
                filters.append(extract(column, 'day') == v)
            elif comparison == "month":
                filters.append(extract(column, 'month') == v)
            elif comparison == "year":
                filters.append(extract(column, 'year') == v)
            elif comparison == "week_date":
                filters.append(extract(column, 'dow') == v)
            elif comparison == "in":
                filters.append(column.in_(v))
            elif comparison == "contains":
                filters.append(column.contains(v))
            elif comparison == "icontains":
                filters.append(column.ilike("%" + v + "%"))
            elif comparison == "startswith":
                filters.append(column.endswith(v))
            elif comparison == "istartswith":
                filters.append(column.ilike(v + "%"))
            elif comparison == "endswith":
                filters.append(column.endswith(v))
            elif comparison == "iendswith":
                filters.append("%" + column.ilike(v))
            elif comparison == "range":
                filters.append(between(column, v[0], v[1]))
            elif comparison == "isnull":
                if v:
                    filters.append(column == None)
                else:
                    filters.append(column != None)
            else:
                raise KeyError("Invalid comparison type %s" % comparison)

        q.query = and_(*filters)

        return q

    def exclude(self, **terms):
        q = self._clone()
        q.query = not_(self.query)
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
        expr = self.model.update().where(self.query).values(**kwargs)
        return self._runquery(expr)

    def delete(self):
        """ Deletes all rows that match the query """
        expr = self.model.delete().where(self.query)
        return self._runquery(expr)

    def exists(self):
        expr = exists().where(self.query)
        return self._runquery(expr)

    def _runquery(self, expression):
        print "_runquery"
        sql = expression.compile()
        print sql
        return defer.succeed([])
        return dbpool.runQuery(sql)

    @defer.inlineCallbacks
    def _iterator(self):
        results = yield self._runquery(select().where(self.query))
        defer.returnValue(results)

    def addBoth(self, callback, *args, **kwargs):
        return self._iterator().addBoth(callback, *args, **kwargs)

