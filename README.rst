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
    Engine.create()

This returns a deferred so you can wait for the table to be created.

Equally, dropping a table looks like this::

    Engine.drop()

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

To create an object and save it one go you can use the ``insert`` method.

    b = yield Blog.insert(name="Ash Blog", tagline="All the latest Ash news")


Filters
=======

Consider you were writing a twisted view::

    class SomeView(HtmlResource):

        @defer.inlineCallbacks
        def content(self, ...):
            rows = yield MyCar.objects.filter(name="Kitt").select()
            for row in rows:
                print row.name, row.mfr, row.date

You can also exclude rows::

    class SomeView(HtmlResource):

        @defer.inlineCallbacks
        def content(self, ...):
            rows = yield MyCar.objects.exclude(name="Kitt").select()
            for row in rows:
                print row.name, row.mfr, row.date


And of course, filters can be chained::

    class SomeView(HtmlResource):

        @defer.inlineCallbacks
        def content(self, ...):
            rows = yield MyCar.objects.filter(name="Kitt").exclude(year=2010).select()
            for row in rows:
                print row.name, row.mfr, row.date


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


