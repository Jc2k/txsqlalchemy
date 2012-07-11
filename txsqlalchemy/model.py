from twisted.internet import defer

import sqlalchemy
from .query import Query
from .connection import Connection, NoConnection
from .columns import BaseColumn, Column, ForeignKey
from . import exceptions

class Objects(object):
    def __init__(self, model):
        self.model = model

    def get_query_set(self):
        return Query(self.model)

    def filter(self, **kwargs):
        return self.get_query_set().filter(**kwargs)

    def exclude(self, **kwargs):
        return self.get_query_set().exclude(**kwargs)

    def all(self):
        return self.get_query_set()

    def count(self):
        return self.get_query_set().count()

    def get(self, **kwargs):
        return self.get_query_set().get(**kwargs)

    def __getitem__(self, idx):
        return self.get_query_set()[idx]


class ModelType(type):

    def __new__(meta, class_name, bases, attrs):
        if class_name == "Base":
            return type.__new__(meta, class_name, bases, attrs)

        attrs["__columns__"] = c = {}
        columns = []
        for attr, col in attrs.items():
            if isinstance(col, BaseColumn):
                columns.append(col.as_column(attr))
                c[attr] = col

        class DoesNotExist(exceptions.DoesNotExist):
             pass
        attrs["DoesNotExist"] = DoesNotExist

        class MultipleObjectsReturned(exceptions.MultipleObjectsReturned):
            pass
        attrs["MultipleObjectsReturned"] = MultipleObjectsReturned

        attrs.setdefault("__tablename__", class_name.lower())
        attrs["__table__"] = t = sqlalchemy.Table(attrs["__tablename__"], bases[0].__metadata__, *columns)
        cls = type.__new__(meta, class_name, bases, attrs)
        cls.objects = Objects(cls)

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
           expr =  self.__table__.update().values(**self._changes)
           column_matches = [c == int(getattr(self, c.name)) for c in self.__table__.primary_key]
           expr = expr.where(sqlalchemy.and_(*column_matches))
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

