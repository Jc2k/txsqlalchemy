
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from txsqlalchemy import Column, String, model_base

class TestSave(TestCase):

    def setUp(self):
        Base = model_base()
        class Foo(Base):
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

    @defer.inlineCallbacks
    def test_create(self):
        Base = model_base()
        Base.bind("sqlite://")
        class Foo(Base):
            a = Column(String)
        yield Foo.create()


class TestDrop(TestCase):

    @defer.inlineCallbacks
    def test_drop(self):
        Base = model_base()
        Base.bind("sqlite://")
        class Foo(Base):
            a = Column(String)
        yield Foo.create()
        yield Foo.drop()


