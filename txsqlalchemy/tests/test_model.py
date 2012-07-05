
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from txsqlalchemy import Model, Column, String
from txsqlalchemy.model import ModelType

class TestSave(TestCase):

    def setUp(self):
        ModelType.reset()

        class Foo(Model):
            a = Column(String)
        self.Model = Foo

    @defer.inlineCallbacks
    def test_save(self):
        foo = self.Model(a='1')
        yield foo.save()

    @defer.inlineCallbacks
    def test_save_no_initargs(self):
        foo = self.Model()
        foo.a = '1'
        yield foo.save()


class TestCreate(TestCase):

    def test_create(self):
        ModelType.reset()

        class Foo(Model):
            a = Column(String)

        Foo.create()


class TestDrop(TestCase):

    def test_drop(self):
        ModelType.reset()

        class Foo(Model):
            a = Column(String)

        Foo.drop()


