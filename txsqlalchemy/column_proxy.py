

class Scalar(object):
    def __init__(self, column):
        self.column = column

    def _construct(self, instance, value):
        self._set(instance, value)

    def _set(self, instance, value):
        instance._changes[self.column.name] = value

    def _get(self, instance):
        return instance._changes[self.column.name]


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


class ForeignChildren(object):

    def __init__(self, column):
        self.column = column

    def _construct(self, instance, value):
        instance._changes[self.column.name] = value

    def _set(self, instance, value):
        raise AttributeError("You cannot assign to a collection")

    def _get(self, instance):
        return ForeignChildrenProxy(instance)


