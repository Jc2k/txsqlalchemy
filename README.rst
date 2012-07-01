============
txsqlalchemy
============

The package provides a lightweight ORM abstraction on top of the sqlalchemy
expression language that is Twisted defer friendly and uses the twisted DB
layer to execute SQL.

It has Django leanings because that's what I like. Sorry.


Table definition
================

You can define a basic table like this::

    from txsqlalchemy import Model, Column, Integer, String

    class MyCar(Model):

        id = Column(Integer, primary_key=True)
        name = Column(String)


Filters
=======

Consider you were writing a twisted view::

    class SomeView(HtmlResource):

        @defer.inlineCallbacks
        def content(self, ...):
            rows = yield MyCar.objects.filter(name="Kitt")

