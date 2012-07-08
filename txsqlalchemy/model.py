from twisted.internet import defer

import sqlalchemy
from .query import Query
from .connection import Connection, NoConnection
from .column_proxy import Scalar, ForeignChildren

class Objects(object):
    def __init__(self, model):
        self.model = model

    def filter(self, **kwargs):
        return Query(self.model).filter(**kwargs)

    def exclude(self, **kwargs):
        return Query(self.model).exclude(**kwargs)

    def all(self):
        return Query(self.model)

    def count(self):
        return self.all().count()


class Column(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def as_column(self, name):
        self.column = sqlalchemy.Column(name, *self.args, **self.kwargs)
        self.name = name
        if self.column.foreign_keys:
            self.proxy = ForeignChildren(self)
        else:
            self.proxy = Scalar(self)
        return self.column

    def _construct(self, instance, value):
        self.proxy._construct(instance, value)

    def __set__(self, instance, value):
        self.proxy._set(instance, value)

    def __get__(self, instance, owner):
        return self.proxy._get(instance)


class ModelType(type):

    def __new__(meta, class_name, bases, attrs):
        if class_name == "Base":
            return type.__new__(meta, class_name, bases, attrs)

        attrs["__columns__"] = c = {}
        columns = []
        for attr, col in attrs.items():
            if isinstance(col, Column):
                columns.append(col.as_column(attr))
                c[attr] = col

        attrs.setdefault("__tablename__", class_name.lower())
        attrs["__table__"] = t = sqlalchemy.Table(attrs["__tablename__"], bases[0].__metadata__, *columns)
        cls = type.__new__(meta, class_name, bases, attrs)
        cls.objects = Objects(cls)

        #cls.__args__ = []
        #for b in bases:
        #    if hasattr(b, "__args__"):
        #        cls.__args__.extend(b.__args__)

        #for key, value in new_attrs.items():
        #    if isinstance(value, Argument):
        #        cls.__args__.append(key)

        return cls


class _Model(object):

    connection = NoConnection()

    def __init__(self, **kwargs):
        self._changes = {}
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._is_new_record = True

    def _construct(self, **kwargs):
        for k, v in kwargs.items():
            self.__columns__[k]._construct(self, v)
        self._is_new_record = False

    @defer.inlineCallbacks
    def save(self):
        if self._is_new_record:
            yield self.insert(**self._changes)
        else:
           #.where(self.query)
           expr =  self.__table__.update().values(**self._changes)
           yield self.connection.run(expr)

        self._changes = {}
        self._is_new_record = False

    @classmethod
    def bind(cls, uri):
        cls.connection = Connection(uri)

    @classmethod
    def create(cls):
        from sqlalchemy.schema import CreateTable
        sql = CreateTable(cls.__table__)
        return cls.connection.run(sql)

    @classmethod
    def drop(cls):
        from sqlalchemy.schema import DropTable
        sql = DropTable(cls.__table__)
        return cls.connection.run(sql)

    @classmethod
    def insert(cls, **kwargs):
        expression = cls.__table__.insert().values(**kwargs)
        return cls.connection.run(expression)


def model_base():
    class Base(_Model):
        __metadata__ = sqlalchemy.MetaData()
        __metaclass__ = ModelType

    return Base

