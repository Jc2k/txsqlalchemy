
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

    def __new__(meta, class_name, bases, attrs):
        if class_name == "Base":
            return type.__new__(meta, class_name, bases, attrs)

        columns = []
        for attr, col in attrs.items():
            if isinstance(col, Column):
                c = sqlalchemy.Column(attr, *col.args, **col.kwargs)
                columns.append(c)
                del attrs[attr]

        attrs.setdefault("__tablename__", class_name.lower())
        attrs["__table__"] = t = sqlalchemy.Table(attrs["__tablename__"], bases[0].__metadata__, *columns)
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


class _Model(object):

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


def model_base():
    class Base(_Model):
        __metadata__ = sqlalchemy.MetaData()
        __metaclass__ = ModelType

    return Base

