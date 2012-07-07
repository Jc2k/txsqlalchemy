
from twisted.trial.unittest import TestCase
from twisted.internet import defer
from txsqlalchemy import Column, DateTime, String, Integer, model_base
import datetime

class TestFiltering(TestCase):

    @defer.inlineCallbacks
    def setUpModel(self):
        Base = model_base()
        Base.bind("sqlite://")
        class FooBar(Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            date = Column(DateTime)
        yield FooBar.create()
        yield FooBar.insert(name = "John", date=datetime.date(year=1900, month=1, day=12))
        yield FooBar.insert(name = "Alex", date=datetime.date(year=2005, month=1, day=1))
        yield FooBar.insert(name = "Timothy", date=datetime.date(year=1900, month=5, day=1))
        yield FooBar.insert(name = "Peter", date=datetime.date(year=1900, month=3, day=5))
        defer.returnValue(FooBar)

    @defer.inlineCallbacks
    def test_simple(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name = "John").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_exact(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__exact="John").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_day(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__day = 5).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Peter")

    @defer.inlineCallbacks
    def test_month(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__month = 5).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Timothy")

    @defer.inlineCallbacks
    def test_year(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__year = 2005).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_week_date(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__week_date = 5).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_in(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id__in=(1,2,3)).select()
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")
        self.assertEqual(results[2].name, "Timothy")

    @defer.inlineCallbacks
    def test_contains(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__contains='oh').select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    #@defer.inlineCallbacks
    #def test_contains_is_case_sensitive(self):
    #    FooBar = yield self.setUpModel()
    #    results = yield FooBar.objects.filter(name__contains='OH').select()
    #    self.assertEqual(len(results), 0)

    @defer.inlineCallbacks
    def test_icontains(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__icontains='OH').select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_startswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__startswith = "J").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_istartswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__istartswith = "j").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_endswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__endswith = "n").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_iendswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__iendswith = "N").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_range(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id__range = (0, 20)).select()
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")
        self.assertEqual(results[2].name, "Timothy")
        self.assertEqual(results[3].name, "Peter")

    @defer.inlineCallbacks
    def test_isnull(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__isnull = True).select()
        self.assertEquals(len(results), 0)

    @defer.inlineCallbacks
    def test_notisnull(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__isnull = False).select()
        self.assertEquals(len(results), 4)


class TestChain(TestCase):

    @defer.inlineCallbacks
    def setUpModel(self):
        Base = model_base()
        Base.bind("sqlite://")
        class FooBar(Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            date = Column(DateTime)
        yield FooBar.create()
        yield FooBar.insert(name = "John", date=datetime.date(year=1900, month=1, day=12))
        yield FooBar.insert(name = "Alex", date=datetime.date(year=2005, month=1, day=1))
        defer.returnValue(FooBar)

    @defer.inlineCallbacks
    def test_filter_then_exclude(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id__range = (0, 20)).exclude(id=2).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_exclude_then_filter(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.exclude(id=1).filter(id__range = (0, 20)).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_filter_then_filter(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id=2).filter(id__range = (0, 20)).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_exclude_then_exclude(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.exclude(id=1).exclude(id__range = (0, 20)).select()
        self.assertEqual(len(results), 0)


class TestCount(TestCase):

    @defer.inlineCallbacks
    def test_case(self):
        Base = model_base()
        Base.bind("sqlite://")
        class FooBar(Base):
            id = Column(Integer, primary_key=True)
        yield FooBar.create()
        yield FooBar.insert()
        yield FooBar.insert()
        count = yield FooBar.objects.count()
        self.assertEquals(count, 2)


