

class BaseException(Exception):
    pass


class DoesNotExist(BaseException):
    """
    A query that was expected to return a single row instead returned 0 rows
    """


class MultipleObjectsReturned(BaseException):
    """
    A query that was expected to returned a single row instead returned multiple rows
    """

