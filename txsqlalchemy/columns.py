
import sqlalchemy


class BaseColumn(object):

    def _construct(self, instance, value):
        instance._changes[self.name] = value

    def as_column(self, name):
        self.column = sqlalchemy.Column(name, *self.args, **self.kwargs)
        self.name = name
        return self.column


class Column(BaseColumn):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __set__(self, instance, value):
        instance._changes[self.name] = value

    def __get__(self, instance, owner):
        return instance._changes[self.name]


class ForeignChildrenProxy(object):

    def __init__(self, model):
        self.model = model

    def get_query_set(self):
        return self.model.objects.filter(id=1)

    def filter(self, **kwargs):
        return self.get_query-set().filter(**kwargs)

    def exclude(self, **kwargs):
        return self.get_query_set().exclude(**kwargs)

    def all(self):
        return self.get_query_set().all()

    def count(self):
        return self.get_query_set().count()


class ForeignKey(object):

    def __init__(self, *args, **kwargs):
        self.args = [sqlalchemy.Integer, sqlalchemy.ForeignKey(args[0])] + list(args[1:])
        self.kwargs = kwargs

    def __set__(self, instance, value):
        raise AttributeError("Cannot assign to collections")

    def __get__(self, instance, owner):
        return ForeignChildrenProxy(instance)

