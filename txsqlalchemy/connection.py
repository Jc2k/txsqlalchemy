import urlparse
from twisted.enterprise import adbapi 

class Connection(object):

    def __init__(self, uri):
        parsed = urlparse.urlparse(uri)

        args = []
        if parsed.scheme in ("sqlite", "sqlite3"):
            args.append("sqlite3")
            if not parsed.path:
                args.append(":memory:")
            else:
                args.append(parsed.path)

            from sqlalchemy.dialects.sqlite import dialect
            self.dialect = dialect()

        self.pool = adbapi.ConnectionPool(*args)

    def run(self, sql, params=None, *args, **kwargs):
        if self.dialect.positional and params:
            args = []
            for k in sql.positiontup:
                args.append(params[k])
            params = args
        return self.pool.runQuery(sql, params, *args, **kwargs)


class NoConnection(object):

    @property
    def dialect(self):
        raise ValueError("Not bound to a database")

    def run(self, sql, *args, **kwargs):
        raise ValueError("Not connected to a database")

