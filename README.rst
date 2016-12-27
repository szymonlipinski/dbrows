DBRows: SQL Database Access With a Nice Interface
=================================================

DBRows is a simple library for accessing SQL database.

Currently is if tested only on PostgreSQL using Psycopg2.
However it uses pure DBAPI 2.0 interface, so it should work on other databases as well.


Installation
------------

To install dbrows, just write:

.. code-block:: bash

    $ pip install dbrows

Examples
---------

The library was written with one thing in mind: create a nice interface for databases.

The simplest example of running a query is:

.. code-block:: python

    from dbrows import Database
    db = Database("postgresql://user:pass@localhost:5432/dbname")
    row = db.query("SELECT 1").first
    print(row[0])


However we can do a little bit more advanced things like automatically closing the connection
(or just releasing it to some connection pool):

.. code-block:: python

    from dbrows import Database
    with Database("postgresql://user:pass@localhost:5432/dbname") as db:
        row = db.query("SELECT 1").first
        print(row[0])

Let's also query with arguments:

.. code-block:: python

    from dbrows import Database
    with Database("postgresql://user:pass@localhost:5432/dbname") as db:
        row = db.query("SELECT a, b, c FROM tab WHERE something > %s ORDER BY a, b", 30).first
        print(row[0])

You can also iterate through all the rows, btw you can also use the column names, not only
the column indexes:

.. code-block:: python

    from dbrows import Database
    with Database("postgresql://user:pass@localhost:5432/dbname") as db:
        for row in db.query("SELECT a, b, c FROM tab WHERE something > %s ORDER BY a, b", 30):
            print(row['a'])
            print(row['b'])

What about transactions? Let's automatically commit:

.. code-block:: python

    from dbrows import Database
    with Database("postgresql://user:pass@localhost:5432/dbname") as db:
        with db.transaction:
            for row in db.query("SELECT a, b, c FROM tab WHERE something > %s ORDER BY a, b", 30):
                print(row['a'])
                print(row['b'])

Or even rollback, e.g. if you want to test something:

.. code-block:: python

    from dbrows import Database
    with Database("postgresql://user:pass@localhost:5432/dbname") as db:
        with db.transaction(rollback=True):
            for row in db.query("SELECT a, b, c FROM tab WHERE something > %s ORDER BY a, b", 30):
                print(row['a'])
                print(row['b'])

And of course you don't need to use `with` everywhere:

.. code-block:: python

    from dbrows import Database
    db = Database("postgresql://user:pass@localhost:5432/dbname")
    transaction = db.transaction
    rows = db.query("SELECT a, b, c FROM tab WHERE something > %s ORDER BY a, b", 30)
    for row in rows:
        print(row['a'])
        print(row['b'])
    transaction.rollback()
    db.close()




Design Decisions
----------------

It's nice to have all things automated, and automatically closed database connection, or a transaction.
That's why the classes like `Transaction` and `Database` have support for the `with` statement.

There are nouns, and verbs. Nouns are for naming some things. Verbs are for doing something with the things.
Having this in mind, I really don't like class methods like `first()`. This should be rather named
`get_first()`. Do we really want to have the getters everywhere? I don't, that's why I rather use
properties. So instead of `rows.get_first()` or `rows.first()` I rather write `rows.first`.
What is going on in the background can be ugly and unpleasant. That really doesn't matter,
for the end user two things are important: the interface, and the code stability.

But of course there are actions like `Database.commit()` or `Database.query()`.
