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

filter(**kwargs)
    Returns a new Queryset containing objects that match the given kwargs
exclude(**kwargs)
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
iexact
    Case insensitive exact match. 
contains
startswith
endswith
in
gt
gte
lt
lte
range
    Match values betwwen a range (inclusive). Example::

        cars = yield Car.objects.filter(year__between=(1982, 1986))

year
    This is only valid on date fields and lets you filter on just the year
    component of the date::

        entries = yield Entry.objects.filter(pub_date__year=2005)

month
    This is only valid on date fields and lets you filter on just the month
    component of the date::

        entries = yield Entry.objects.filter(pub_date__month=2005)

day
    This is only valid on date fields and lets you filter on just the day
    component of the date::

        entries = yield Entry.objects.filter(pub_date__day=2005)

week_day
    This is only valid on date fields and lets you filter on just the week day
    of the date::

        entries = yield Entry.objects.filter(pub_date__week_day=6)

isnull
    If you pass ``True`` it will filter for ``NULL`` rows, and for ``False`` it will filter for ``NOT NULL``::

        entries = yield Entry.objects.filter(pub_date__isnull=True)


Limiting results
----------------

You can use the Python slice syntax to limit your Query to a certain number of
results. These map to the SQL ``LIMIT`` and ``OFFSET`` clauses.

To only fetch the first 5 objects::

    cars = yield Car.objects.all()[:5]

To fetch the 6th and 7th object::

    cars = yield Car.objects.all()[5:7]

Negative indexing is not supported.


Updates
=======

You can write an update query::

    @defer.inlineCallbacks
    def update_some_things():
        yield MyCar.objects.filter(name="Kitt").update(cpu="Arm Cortex")


Delete
======

You can delete stuff::

    @defer.inlineCallbacks
    def delete_some_things():
        yield MyCar.objects.filter(type="SUV").delete()
        print "All SUV's have been from the world"


