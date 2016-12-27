# -*- coding: utf-8 -*-
from collections import OrderedDict


class WrongOperationError(Exception):
    pass


class Row(object):
    """A row from a database.


    Parameters
    ----------
    col_names : List[str]
        Names of the columns for the row data
    values : List[str]
        Values for the row.


    Examples
    --------
    The row fields can be accessed using 0 based indexes:
        row[0]
    or using the column names:
        row['first']

    """

    def __init__(self, col_names, values):
        assert len(col_names) == len(values)
        self._dict = OrderedDict([(name, value) for name, value in zip(col_names, values)])

    @property
    def values(self):
        """tuple: Values of the row in the same order as inserted."""
        return tuple(self._dict.values())

    @property
    def col_names(self):
        """tuple: Names of the columns of the row in the same order as inserted."""
        return tuple(self._dict.keys())

    @property
    def as_dict(self):
        """dict: The row as a dictionary."""
        return self._dict

    @property
    def size(self):
        """int: Number of the columns in the row."""
        return len(self._dict)

    def __getattr__(self, name):
        try:
            return self._dict[name]
        except KeyError:
            raise AttributeError("'{0}' has no attribute '{1}'".format(self, name))

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.values[item]
        if isinstance(item, basestring):
            return self._dict[item]

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<Row {}>'.format(self.as_json)

    @property
    def as_json(self):
        """str: The row as a JSON string."""
        import json
        from decimal import Decimal

        def default(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            else:
                return obj

        return json.dumps(self._dict, default=default, sort_keys=True)


class RowCollection(object):
    """Collection of rows.


    Notes
    -----
    The collection is lazy, all the rows are downloaded when needed.
    Nothing is cached, all data is returned.


    Parameters
    ----------
    cursor : DBAPI.connection.cursor
        Opened database cursor with the query results.
    col_names : List[str]
        Names of the columns returned by the query.


    Examples
    --------
    The row fields can be accessed using 0 based indexes:
        row[0]
    or using the column names:
        row['first']

    """

    def __init__(self, cursor, col_names):
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
        """Row or None: Returns the first row from the result set.

        Notes
        -----
        When called multiple times, it returns the same data.
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

    def __init__(self, database, rollback=None, commit=None):
        if rollback and commit:
            raise ValueError("Cannot set rollback and commit at the same time.")

        self._database = database
        self._rollback = rollback
        self._commit = commit
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self._closed = True

        if exc_type:
            self._database.rollback()

        if self._commit:
            self._database.commit()
        if self._rollback:
            self._database.rollback()

    def __call__(self, rollback=None, commit=None):
        if rollback and commit:
            raise ValueError("Cannot set rollback and commit at the same time.")
        self._rollback = rollback
        self._commit = commit
        return self

    def __repr__(self):
        return "<Transaction closed:{} commit:{} rollback:{}>".format(self._closed, self._commit, self._rollback)

    @property
    def closed(self):
        return self._closed


class Database(object):
    """Connection to a database"""

    def __init__(self, connstr):
        self._connstr = connstr
        self._open = True
        self._col_names = None

        if self._connstr.startswith('postgresql://'):
            import psycopg2 as dbapi
            self._dbapi = dbapi
        elif self._connstr.startswith('sqlite://'):
            import sqlite3 as dbapi
            self._dbapi = dbapi
            self._connstr = self._connstr.replace('sqlite://', '')

        self._connection = self._dbapi.connect(self._connstr)

    @property
    def open(self):
        return self._open

    def query(self, query_str, *params):
        """Makes a query, and returns the results."""
        cursor = self._connection.cursor()
        cursor.execute(query_str, tuple(params))

        self._col_names = None
        if cursor.description is not None:
            self._col_names = tuple([col.name for col in cursor.description])
        return RowCollection(cursor=cursor, col_names=self._col_names)

    def close(self):
        """Closes the database connection."""
        self._open = False
        self._connection.close()

    def begin(self):
        """Starts a transaction."""
        self._connection.begin()

    def commit(self):
        """Commits a transaction."""
        self._connection.commit()

    def rollback(self):
        """Rolls back a transaction."""
        self._connection.rollback()

    @property
    def transaction(self):
        return Transaction(self, commit=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()









