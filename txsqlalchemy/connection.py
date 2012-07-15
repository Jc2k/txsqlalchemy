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

        self.pool = adbapi.ConnectionPool(*args, cp_min=1, cp_max=1)

    def _bind(self, compiled, dialect):
        compiled_parameters = [compiled.construct_params()]
        parameters = []

        def _paramify(param, key):
            processors = compiled._bind_processors
            if key in processors:
                return processors[key](param[key])
            return param[key]

        if dialect.positional:
            if not hasattr(compiled, "positiontup"):
                return []

            for compiled_params in compiled_parameters:
                param = []
                for key in compiled.positiontup:
                    param.append(_paramify(compiled_params, key))
                parameters.append(dialect.execute_sequence_format(param))
        else:
            encode = dialect._encoder if not dialect.supports_unicode_statements else lambda key: [key]
            for compiled_params in compiled_parameters:
                param = {}
                for key in compiled_params:
                    param[encode(key)[0]] = _paramify(compiled_params, key)
                parameters.append(param)

        return dialect.execute_sequence_format(parameters)

    def run(self, expression, retval="selected"):
        compiled = expression.compile(dialect=self.dialect)
        bound = self._bind(compiled, self.dialect)
        bound = bound[0] if bound else []
        def _run(cursor, sql, vars):
            rows = cursor.execute(sql, vars)
            if retval == "lastrowid":
                return cursor.lastrowid
            return [r for r in rows]
        #print str(compiled), bound
        return self.pool.runInteraction(_run, str(compiled), bound)


class NoConnection(object):

    @property
    def dialect(self):
        raise ValueError("Not bound to a database")

    def run(self, sql, *args, **kwargs):
        raise ValueError("Not connected to a database")

