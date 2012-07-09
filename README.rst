============
txsqlalchemy
============

I couldn't find a nice way to do SQLite or Postgres in Twisted. For me, nice is
the Django ORM. But without that settings.py stuff. And that integrates nicely
with twisted Deferred's and ideally ``twisted.enterprise.adapi``.

The package provides a lightweight ORM abstraction on top of the sqlalchemy
expression language that is Twisted defer friendly and uses the twisted DB
layer to execute SQL.

It has Django leanings because that's what I like. Sorry.

Any examples below where you see use of ``yield`` is a situation where
txsqlalchemy returns a Deferred or Deferred like objects. You can use
``addCallback`` to build asynchronous database operations. Within a function
decorated with ``defer.inlineCallbacks`` you can yield as the examples do.


Table definition
================

You can define a basic table like this::

    from txsqlalchemy import model_base, Column, Integer, String

    Base = model_base()

    class MyCar(Base):

        id = Column(Integer, primary_key=True)
        name = Column(String)


Managing your database
======================

You can create a table like this::

    class Engine(Base):
        size = Column(String)
    yield Engine.create()

This returns a deferred so you can wait for the table to be created.

Equally, dropping a table looks like this::

    yield Engine.drop()

And again.. it returns a deferred.


Creating objects
================

Import the model class you wanted to create objects from and pass it kwargs.
Call ``save`` to asychronously commit to the database::

    from .models import Blog
    b = Blog(name="Ash Blog", tagline="All the latest Ash news")
    yield b.save()

Behind the scenes this will trigger an ``INSERT`` SQL query. This happens when
(and only when) you explicitly call ``save``.

The ``save`` method returns a ``Deferred``. The callback doesn't have a specifc
return value.

To create an object and save it one go you can use the ``insert`` method::

    b = yield Blog.insert(name="Ash Blog", tagline="All the latest Ash news")


Querying
========

Like Django txsqlalchemy has a Manager object on each model for table-level
operations. By default it is called ``objects``.

Retrieving all objects is simple - you ask the Manager for ``all()``. It gives
you a deferred which will eventually give you a list of objects you require::

    all_entries = yield Entry.objects.all()

If you don't yield the object it will continue to act as a Queryset and you can
continue to apply filters to it.

To get a subset of rows, use the you can use the following object manager methods:

filter(\*\*kwargs)
    Returns a new Queryset containing objects that match the given kwargs
exclude(\*\*kwargs)
    Returns a new Queryset containing objects that do *not* match the given kwargs

For example::

    cars = yield MyCar.objects.filter(name="Kitt")

The result of a filter or exclude operation is a queryset, which can be further
filtered. This is called chaining::

    cars = yield MyCar.objects.filter(name="Kitt").exclude(year=2010)

Each time you apply a filter a brand-new Queryset is created.

Querys are lazy. Creating or refiing a query doesn't involve any database
activity.

Filters
-------

The parameters you pass to `` filter`` and ``exclude`` can be just exact matches like this::

    cars = yield Car.objects.filter(name="Kitt")

But they can also be one of several over lookup types. For example::

    cars = yield Car.objects.filter(year__lt = 2010)

Here are the built in lookup types.

exact
    An exact equals match. This is the default if you don't specify a lookup type.

    This generates SQL like::

        SELECT ... WHERE name = 'Kitt';

    There is a case insensitive version you can use::

        cars = yield Car.objects.filter(name__iexact="kitt") 

contains
    Matches if a field contains the string passed to the filter::

        cars = yield Car.objects.filter(name__contains="it")

    This generates SQL like::

        SELECT .. WHERE name LIKE '%it%';

    There is a case insensitive version you can use - ``icontains``.

    When using SQLite remember that SQLite doesn't support case sensitive
    ``LIKE`` statements. In that case, ``contains`` will have the same
    behaviour as ``icontains``.

startswith
    Matches if a field starts with the string passed to the filter::

        cars = yield Car.objects.filter(name__startswith="K")

    This generates SQL like::

        SELECT ... WHERE name LIKE 'K%';

    There is a case insensitive version you can use - ``istartswith``.

    When using SQLite remember that SQLite doesn't support case sensitive
    ``LIKE`` statements. In that case, ``startswith`` will have the same
    behaviour as ``istartswith``.

endswith
    Matches if a field ends with the string passed to the filter::

        cars = yield Car.objects.filter(name__startswith="tt")

    This generates SQL like::

        SELECT ... WHERE name LIKE '%tt';

    There is a case insensitive version you can use - ``iendswith``.

    When using SQLite remember that SQLite doesn't support case sensitive
    ``LIKE`` statements. In that case, ``endswith`` will have the same
    behaviour as ``iendswith``.

in
    Matches if a field matches exactly one of the items in the list. For
    example, the query::

        cars = yield Car.objects.filter(id__in=[1, 3, 4])

    Which would be equivalent to SQL like::

        SELECT ... WHERE id IN (1, 3, 4);

gt
    Matches if the value of the field is greater than the value passed to the
    filter::

        cars = yield Car.objects.filter(year_gt = 1982)

    This will generate SQL like::

        SELECT ... WHERE year > 1982

gte
    Matches if the value of the field is greater than or equal to the value
    passed to the filter::

        cars = yield Car.objects.filter(year_gte = 1983)

    This will generate SQL like::

        SELECT ... WHERE year >= 1983

lt
    Matches if the value of the field is less than the value passed to the
    filter::

        cars = yield Car.objects.filter(year_lt = 1987)

    This will generate SQL like::

        SELECT ... WHERE year < 1987

lte
    Matches if the value of the field is less than or equal to the value
    passed to the filter::

        cars = yield Car.objects.filter(year_lte = 1986)

    This will generate SQL like::

        SELECT ... WHERE year <= 1986

range
    Match values betwwen a range (inclusive). Example::

        cars = yield Car.objects.filter(year__between=(1982, 1986))

    This will generate SQL like::

        SELECT ... WHERE year BETWEEN 1982 and 1986

year
    This is only valid on date fields and lets you filter on just the year
    component of the date::

        entries = yield Entry.objects.filter(pub_date__year=2005)

    This will generate SQL like::

        SELECT ... WHERE EXTRACT('year' FROM pub_date) = 2005

month
    This is only valid on date fields and lets you filter on just the month
    component of the date::

        entries = yield Entry.objects.filter(pub_date__month=12)

    This will generate SQL like::

        SELECT ... WHERE EXTRACT('month' FROM pub_date) = 12

day
    This is only valid on date fields and lets you filter on just the day
    component of the date::

        entries = yield Entry.objects.filter(pub_date__day=13)

    This will generate SQL like::

        SELECT ... WHERE EXTRACT('day' FROM pub_date) = 13

week_day
    This is only valid on date fields and lets you filter on just the week day
    of the date::

        entries = yield Entry.objects.filter(pub_date__week_day=6)

    This will generate SQL like::

        SELECT ... WHERE EXTRACT('dow' FROM pub_date) = 6

isnull
    If you pass ``True`` it will filter for ``NULL`` rows, and for ``False`` it will filter for ``NOT NULL``::

        entries = yield Entry.objects.filter(pub_date__isnull=True)

    This will generate SQL like::

        SELECT ... WHERE pub_date IS NULL;


Limiting results
----------------

You can use the Python slice syntax to limit your Query to a certain number of
results. These map to the SQL ``LIMIT`` and ``OFFSET`` clauses.

To only fetch the first 5 objects::

    cars = yield Car.objects.all()[:5]

To fetch the 6th and 7th object::

    cars = yield Car.objects.all()[5:7]

Negative indexing is not supported.


Finding a single object
=======================

If you are only expecting a single row to be returned by a query then there is
a ``get`` wrapper. It gives you a deferred that will fire with a **single**
object. This will throw exceptions if no records are found, or if too many
records are found (as ``errback`` if you arent using ``inlineCallbacks``)::

    try:
        kitt = yield Car.objects.get(name="Kitt")
    except Car.DoesNotExist:
        print "No object found"
    except Car.MultipleObjectsReturned:
        print "Too many objects found"

You can use any expression with ``get`` that you would with ``filter``.

Each table has its own ``DoesNotExist`` and ``MultibleObjectsReturned``
exception. They are members of the model class so are available anywhere you
are using the models.


Updates
=======

You can write an update query::

    yield MyCar.objects.filter(name="Kitt").update(cpu="Arm Cortex")


Delete
======

You can delete stuff::

    yield MyCar.objects.filter(type="SUV").delete()

