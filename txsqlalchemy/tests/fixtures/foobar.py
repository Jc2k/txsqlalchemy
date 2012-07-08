from twisted.internet import defer
from .base import Fixture
import datetime
from txsqlalchemy import Column, Integer, String, DateTime

class FooBarBaz(Fixture):

    @defer.inlineCallbacks
    def setUp(self, testcase):
        super(FooBarBaz, self).setUp(testcase)

        class FooBar(self.Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            date = Column(DateTime)
        yield FooBar.create()
        yield FooBar.insert(name = "John", date=datetime.date(year=1900, month=1, day=12))
        yield FooBar.insert(name = "Alex", date=datetime.date(year=2005, month=1, day=1))
        yield FooBar.insert(name = "Timothy", date=datetime.date(year=1900, month=5, day=1))
        yield FooBar.insert(name = "Peter", date=datetime.date(year=1900, month=3, day=5))
        testcase.FooBar = self.FooBar = FooBar


