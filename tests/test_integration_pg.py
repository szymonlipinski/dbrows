from dbrows import Database, RowCollection, Row, WrongOperationError, Transaction
import pytest
import unittest
import psycopg2 as dbapi
from os import environ
from collections import namedtuple
from decimal import Decimal
import datetime


connstr = environ.get("ROWS_DB_TEST")

Table = namedtuple("Table", ['schema', 'name', 'type'])


if connstr is None:
    print("""
    THE TESTS NEED TO CONNECT TO A DATABASE,
    PLEASE SET ROWS_DB_TEST IN YOUR ENVIRONMENT VARIABLES,
    LIKE THIS:
        export ROWS_DB_TEST=postgresql://user:pass@localhost:5432/dbname
    """)
    exit(14)


def tables(db):
    return [Table(schema=t.table_schema, name=t.table_name, type=t.table_type)
            for t in db.query("""
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables
            """)]


def assert_table_exists(db, name):
    assert table_exists(db, name), "Haven't found table '{}'".format(name)


def assert_table_doesnt_exist(db, name):
    assert not table_exists(db, name), "Found the table '{}'".format(name)


def table_exists(db, name):
    rows = db.query("SELECT 42 FROM information_schema.tables WHERE table_name = '{}'".format(name))
    return rows.size == 1


def drop_table_if_exists(db, name):
    if table_exists(db, name):
        db.query("DROP TABLE {}".format(name))
        db.commit()


class TestDatabaseConnection(unittest.TestCase):
    def test_connection(self):
        db = Database(connstr)
        assert db.is_open

        db.close()
        assert not db.is_open

    def test_bad_uri(self):
        try:
            Database("bad uri")
            assert False, "Should get exception"
        except Exception as e:
            pass

    def test_bad_connection(self):
        with pytest.raises(dbapi.OperationalError):
            Database('postgresql://bad:something/nodb')


class TestDatabase(unittest.TestCase):

    def setUp(self):
        with Database(connstr) as db:
            with db.transaction:
                drop_table_if_exists(db, 'test')
                drop_table_if_exists(db, 'trans_test')
            assert_table_doesnt_exist(db, 'test')
            with db.transaction:
                db.query("CREATE TABLE test (i int, t text, v varchar(300), d timestamp, dc decimal)")
                db.query("INSERT INTO test(i, t, v, d, dc) VALUES(1, 'aat', 'aav', '2016-01-01', 0.1)")
                db.query("INSERT INTO test(i, t, v, d, dc) VALUES(2, 'bbt', 'bbv', '2016-02-02', 0.2)")
                db.query("INSERT INTO test(i, t, v, d, dc) VALUES(3, 'cct', 'ccv', '2016-03-03', 0.3)")
            assert_table_exists(db, 'test')

    def test_calling_first_twice(self):
        db = Database(connstr)
        assert db
        assert db.is_open
        rows = db.query("""SELECT i, t, v, d, dc FROM test""")
        assert rows.first == rows.first
        assert rows.first is rows.first

    def test_simple_db_query(self):
        with Database(connstr) as db:
            assert db.is_open
            rows = db.query("""SELECT i, t, v, d, dc FROM test WHERE i = 1""")
            assert rows
            assert isinstance(rows, RowCollection)
            assert repr(rows) == '<RowCollection size=1 pending=1>'
            assert len(rows) == 1
            assert rows.pending == 1
            assert rows.size == 1
            row = rows.first
            assert isinstance(row, Row)
            assert len(row) == 5
            assert row.size == 5
            assert row[0] == 1
            assert row[1] == 'aat'
            assert row[2] == 'aav'
            assert row[3] == datetime.datetime(2016, 1, 1, 0, 0)
            assert row[4] == Decimal('0.1')
            assert isinstance(row.values, tuple)
            assert isinstance(row.col_names, tuple)
            assert row.values == (1, 'aat', 'aav', datetime.datetime(2016, 1, 1, 0, 0), Decimal('0.1'))
            assert row.col_names == ('i', 't', 'v', 'd', 'dc')
            assert len(rows) == 1
            assert rows.pending == 0
            assert rows.size == 1
            assert repr(rows) == '<RowCollection size=1 pending=0>'

    def test_empty_rowset(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 WHERE false""")
            assert not rows
            assert len(rows) == 0
            assert repr(rows) == '<RowCollection size=0 pending=0>'
            assert rows.first is None

    def test_iterating_empty_rowset(self):
        with Database(connstr) as db:
            for row in db.query("""SELECT 1 WHERE false"""):
                assert False, "Shouldn't get here"

    def test_iterating_one_row_rowset(self):
        with Database(connstr) as db:
            for row in db.query("""SELECT i, t, v FROM test WHERE i = 2"""):
                assert isinstance(row, Row)
                assert len(row) == 3
                assert row.size == 3
                assert row[0] == 2
                assert row[1] == 'bbt'
                assert row[2] == 'bbv'
                assert isinstance(row.values, tuple)
                assert isinstance(row.col_names, tuple)
                assert row.values == (2, 'bbt', 'bbv')
                assert row.col_names == ('i', 't', 'v')

    def test_iterating_after_first(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)

            first = rows.first

            assert first.values == (1, 'two', 3.0)
            assert first.col_names == ('c_one', 'c_two', 'c_three')

            for row in rows:
                assert row == first
                assert row is first


    def test_row_as_dict(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)
            first = rows.first
            assert first.values == (1, 'two', 3.0)
            assert first.col_names == ('c_one', 'c_two', 'c_three')

            fd = first.as_dict
            assert isinstance(fd, dict)
            assert sorted(fd.keys()) == sorted(list(first.col_names))
            assert list(fd.values()) == list(first.values)

    def test_row_as_json(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)
            first = rows.first
            assert first.values == (1, 'two', 3.0)
            assert first.col_names == ('c_one', 'c_two', 'c_three')

            fd = first.as_json
            assert fd == '{"c_one": 1, "c_three": "3.0", "c_two": "two"}'
            assert isinstance(fd, str)

    def test_iterating_query_with_arguments(self):
        """
        db.query("CREATE TABLE test (i int, t text, v varchar(300), d timestamp, dc decimal)")
        db.query("INSERT INTO test(i, t, v, d, dc) VALUES(1, 'aat', 'aav', '2016-01-01', 0.1)")
        db.query("INSERT INTO test(i, t, v, d, dc) VALUES(2, 'bbt', 'bbv', '2016-02-02', 0.2)")
        db.query("INSERT INTO test(i, t, v, d, dc) VALUES(3, 'cct', 'ccv', '2016-03-03', 0.3)")
        """
        with Database(connstr) as db:
            for row in db.query("""select i, dc from test where i = %s or i = %s""", 2, 3):

                drow = row.as_dict
                i, dc = drow['i'], drow['dc']
                assert len(row) == 2
                assert dc == Decimal('0.{}'.format(i))
                assert repr(row) == '<Row {"dc": "%s", "i": %s}>' % (dc, i)

    def test_query_results_with_arguments_multiple_rows(self):
        with Database(connstr) as db:
            rows = db.query("""select i, dc from test where i = %s or i = %s""", 2, 3)

            assert rows.pending == 2
            assert rows.size == 2
            assert str(rows) == '<RowCollection size=2 pending=2>'

            first = rows.first
            assert first is not None
            assert len(first) == 2
            assert first[0] == 2
            assert first[1] == Decimal('0.2')
            assert first['i'] == 2
            assert first['dc'] == Decimal('0.2')

    def test_transaction(self):
        with Database(connstr) as db:
            drop_table_if_exists(db, 'trans_test')
            with db.transaction as t:
                assert not t.closed
                db.query("CREATE TABLE trans_test (i integer);")

            assert t.closed
            assert_table_exists(db, 'trans_test')

    def test_transaction_commit(self):
        with Database(connstr) as db:
            drop_table_if_exists(db, 'trans_test')
            with db.transaction(commit=True) as t:
                assert not t.closed
                db.query("CREATE TABLE trans_test (i integer);")

            assert t.closed
            assert_table_exists(db, 'trans_test')

    def test_transaction_rollback(self):
        with Database(connstr) as db:
            drop_table_if_exists(db, 'trans_test')
            with db.transaction(rollback=True) as t:
                db.query("CREATE TABLE trans_test (i integer);")

            assert_table_doesnt_exist(db, 'trans_test')

    def test_transaction_block_rollback_and_commit(self):
        with Database(connstr) as db:
            with pytest.raises(ValueError):
                with db.transaction(rollback=True, commit=True):
                    pass

    def test_transaction_object_rollback_and_commit(self):
        with Database(connstr) as db:
            with pytest.raises(ValueError):
                db.transaction(rollback=True, commit=True)
