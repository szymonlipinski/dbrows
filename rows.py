# -*- coding: utf-8 -*-
import psycopg2 as dbapi

class WrongOperationError(Exception):
    pass

class Row(object):
    """A row from database"""

    def __init__(self, col_names, values):
        """
        :param col_names: Tuple with column names
        :param values: Tuple with values for this row.
        """
        self._col_names = col_names
        self._values = values

        if values is not None:
            assert len(col_names) == len(values)

    @property
    def values(self):
        return self._values

    @property
    def col_names(self):
        return self._col_names

    @property
    def as_dict(self):
        return {name:value for name, value in zip(self.col_names, self.values)}

    @property
    def size(self):
        return len(self._values)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._values[item]

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        return '<Row {}>'.format("?")

    @property
    def as_json(self):
        import json
        from decimal import Decimal

        def default(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            else:
                return obj

        return json.dumps(self.as_dict, default=default)


class RowCollection(object):
    """Collection of rows"""

    def __init__(self, cursor, col_names):
        """

        :param cursor: Cursor for reading the data from.
        :param col_names: Tuple of column names.
        :param cache_all_rows: If True, then the RowCollection will keep all rows in memory,
                               so the iterator can be reused without making the query again.
        """
        self._cursor = cursor
        self._col_names = col_names

        self._size = self._cursor.rowcount
        self._pending = self._cursor.rowcount

        self._got_first = None
        self._first_row = None

        self._rows_buffer = None  # used for keeping raw objects read by the __iter__()

    def __repr__(self):
        return "<RowCollection size={} pending={}>".format(self._cursor.rowcount, self._pending)

    def __len__(self):
        return self._size

    @property
    def first(self):
        """Gets the first row from the result set.

        :return: Row or None when the set is empty.
        """
        if not self._got_first:
            data = self._cursor.fetchone()
            self._got_first = True
            if data:
                self._pending -= 1
                self._first_row = Row(col_names=self._col_names, values=data)
            else:
                self._first_row = None

        return self._first_row

    @property
    def pending(self):
        return self._pending

    def __iter__(self):
        while True:
            self._rows = self._cursor.fetchmany(10)
            if not self._rows:
                break
            for row in self._rows:
                yield Row(col_names=self._col_names, values=row)

    @property
    def size(self):
        return self._size


class Transaction(object):
    """Database transaction."""

    def __init__(self, database, rollback=True, commit=True):
        self._database = database
        self._rollback = rollback
        self._commit = commit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._commit:
            self._database.comit()
        elif self._rollback:
            self._database.rollbac()


class Database(object):
    """Connection to a database"""

    def __init__(self, connstr):
        self._connstr = connstr
        self._open = True
        self._col_names = None

        if self._connstr.startswith('postgresql://'):
            pass

        self._connection = dbapi.connect(self._connstr)

    @property
    def open(self):
        return self._open

    def query(self, query_str, cache_all_rows=False):
        """Makes a query, and returns the results."""
        cursor = self._connection.cursor()
        cursor.execute(query_str)
        self._col_names = tuple([col.name for col in cursor.description])
        return RowCollection(cursor=cursor, col_names=self._col_names)

    def close(self):
        """Closes the database connection."""
        self._open = False
        self._connection.close()

    def begin(self):
        """Starts a transaction."""
        pass

    def commit(self):
        """Commits a transaction."""
        pass

    def rollback(self):
        """Rolls back a transaction."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()





