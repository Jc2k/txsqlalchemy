
import sqlalchemy
from .query import Query

class Objects(object):
    def __init__(self, model):
        self.model = model

    def filter(self, **kwargs):
        return Query(self.model).filter(**kwargs)

    def exclude(self, **kwargs):
        return Query(self.model).exclude(**kwargs)


class Column(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class ModelType(type):

    # FIXME: This limits us to one database connection or something?
    # Meh. One database pubbot is terrifying enough.
    metadata = sqlalchemy.MetaData()

    def __new__(meta, class_name, bases, attrs):
        columns = []
        for attr, col in attrs.items():
            if isinstance(col, Column):
                c = sqlalchemy.Column(attr, *col.args, **col.kwargs)
                columns.append(c)
                del attrs[attr]

        attrs.setdefault("__tablename__", class_name.lower())
        attrs["__table__"] = t = sqlalchemy.Table(attrs["__tablename__"], meta.metadata, *columns)
        attrs["objects"] = Objects(t)

        cls = type.__new__(meta, class_name, bases, attrs)

        #cls.__args__ = []
        #for b in bases:
        #    if hasattr(b, "__args__"):
        #        cls.__args__.extend(b.__args__)

        #for key, value in new_attrs.items():
        #    if isinstance(value, Argument):
        #        cls.__args__.append(key)

        return cls

    @staticmethod
    def reset():
        ModelType.metadata = sqlalchemy.MetaData()


class Model(object):

    __metaclass__ = ModelType

    def __init__(self, **kwargs):
        pass

    def save(self):
        pass

    @classmethod
    def create(cls):
        from sqlalchemy.schema import CreateTable
        sql = CreateTable(cls.__table__).compile()

    @classmethod
    def drop(cls):
        from sqlalchemy.schema import DropTable
        sql = DropTable(cls.__table__).compile()

