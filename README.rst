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

And of course you don't need to use ``with`` everywhere:

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

Support of With
~~~~~~~~~~~~~~~

It's nice to have all things automated. Something like automatically closed database connection,
or automatically committed transaction.
That's why the classes like ``Transaction`` and ``Database`` have support for the ``with`` statement.
The great thing about ``with`` is that you really don't have to use it.

Properties and Actions
~~~~~~~~~~~~~~~~~~~~~~

Do we really want to have the getters everywhere? I don't, that's why I rather use
properties when appropriate.
So instead of ``rows.get_first()`` or ``rows.first()`` I rather write ``rows.first``.
What is going on in the background can be ugly and unpleasant. That really doesn't matter.

For the end user two things are important: **the interface**, and **the code stability**.

But of course there are actions like ``Database.commit()`` or ``Database.query()``.

There are **nouns**, and **verbs**.
Nouns are for naming things.
Verbs are for doing something with the things.
So generally: **Noun - a thing**; **Verb - an activity**.

Having this in mind, I really don't like class methods like ``first()``. This should be rather named
``get_first()``. This way the interface for the ``Row`` class should be:

.. code-block:: python

    row.get_values()
    row.get_col_names()
    row.get_size()
    row.get_as_dict()
    row.get_as_json()

Or even something worse: let's mix it. Mix the functions, and properties like this:

.. code-block:: python

    # PROPERTIES:
    row.values
    row.col_names
    row.size

    # FUNCTIONS
    row.as_dict()
    row.as_json()

Good luck with remembering which one is a property, which one is a function.

I want to have simple interfaces. The ``Row`` class is just a pure container, has some data inside,
and only returns it. There is some logic of course, but should be hidden. The ``Row`` class
has only properties, with Nouns:

.. code-block:: python

    row.values
    row.col_names
    row.size
    row.as_dict
    row.as_json

However for the ``Database`` class there are some actions. The interface is:

.. code-block:: python

    # a flag, property of course
    db.is_open

    # a simple property returning a Transaction object
    db.transaction

    # an action, makes a query
    query(query_str, *params)

    # an action, closes database connection
    close()

    # an action, starts a transaction
    begin()

    # an action, commits a transaction
    commit()

    # an action, rolls back a transaction
    rollback()




