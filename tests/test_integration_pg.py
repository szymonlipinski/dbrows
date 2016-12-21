from rows import Database, RowCollection, Row, WrongOperationError
import pytest
import unittest
import psycopg2 as dbapi

connstr = "postgresql://rows:rows@localhost:5496/rows"


class TestDatabase(unittest.TestCase):

    def test_connection(self):
        db = Database(connstr)
        assert db.open

        db.close()
        assert not db.open

    def test_bad_uri(self):
        with pytest.raises(dbapi.OperationalError):
            Database("bad uri")

    def test_bad_connection(self):
        with pytest.raises(dbapi.OperationalError):
            Database('postgresql://bad:something/nodb')

    def test_calling_first_twice(self):
        db = Database(connstr)
        assert db
        assert db.open
        rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)
        assert rows.first == rows.first
        assert rows.first is rows.first

    def test_simple_db_query(self):
        with Database(connstr) as db:
            assert db.open
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)
            assert rows
            assert isinstance(rows, RowCollection)
            assert repr(rows) == '<RowCollection size=1 pending=1>'
            assert len(rows) == 1
            assert rows.pending == 1
            assert rows.size == 1
            row = rows.first
            assert isinstance(row, Row)
            assert len(row) == 3
            assert row.size == 3
            assert row[0] == 1
            assert row[1] == 'two'
            assert row[2] == 3.0
            assert isinstance(row.values, tuple)
            assert isinstance(row.col_names, tuple)
            assert row.values == (1, 'two', 3.0)
            assert row.col_names == ('c_one', 'c_two', 'c_three')
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
            for row in db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """):
                assert isinstance(row, Row)
                assert len(row) == 3
                assert row.size == 3
                assert row[0] == 1
                assert row[1] == 'two'
                assert row[2] == 3.0
                assert isinstance(row.values, tuple)
                assert isinstance(row.col_names, tuple)
                assert row.values == (1, 'two', 3.0)
                assert row.col_names == ('c_one', 'c_two', 'c_three')

    def test_iterating_after_first(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)

            first = rows.first

            assert first.values == (1, 'two', 3.0)
            assert first.col_names == ('c_one', 'c_two', 'c_three')

            for row in rows:
                assert row == first
                assert row is first

    def test_first_after_iterating_with_caching(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)

            for row in rows:
                assert row.values == (1, 'two', 3.0)
                assert row.col_names == ('c_one', 'c_two', 'c_three')

            first = rows.first
            assert first is None

    def test_row_as_dict(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)
            first = rows.first
            assert first.values == (1, 'two', 3.0)
            assert first.col_names == ('c_one', 'c_two', 'c_three')

            fd = first.as_dict
            assert isinstance(fd, dict)
            assert sorted(fd.keys()) == sorted(list(first.col_names))
            assert sorted(fd.values()) == sorted(list(first.values))

    def test_row_as_json(self):
        with Database(connstr) as db:
            rows = db.query("""SELECT 1 "c_one", 'two' "c_two", 3.0 "c_three" """)
            first = rows.first
            assert first.values == (1, 'two', 3.0)
            assert first.col_names == ('c_one', 'c_two', 'c_three')

            fd = first.as_json
            assert fd == '{"c_three": "3.0", "c_one": 1, "c_two": "two"}'
            assert isinstance(fd, str)



