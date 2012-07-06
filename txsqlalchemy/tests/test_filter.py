
from twisted.trial.unittest import TestCase
from twisted.internet import defer
from txsqlalchemy import Column, DateTime, String, Integer, model_base

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
        yield FooBar.insert(name = "John")
        yield FooBar.insert(name = "Alex")
        defer.returnValue(FooBar)

    @defer.inlineCallbacks
    def test_simple(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name = "John").select()
        self.assertEqual(len(results), 1)
        #self.assertEqual(results[0], "John")

    @defer.inlineCallbacks
    def test_exact(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__exact="John").select()

    @defer.inlineCallbacks
    def test_day(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__day = 5).select()

    @defer.inlineCallbacks
    def test_month(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__month = 5).select()

    @defer.inlineCallbacks
    def test_year(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__year = 2005).select()

    @defer.inlineCallbacks
    def test_week_date(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__week_date = 5).select()

    @defer.inlineCallbacks
    def test_in(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__in=(1,2,3)).select()

    @defer.inlineCallbacks
    def test_contains(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__contains='oh').select()

    @defer.inlineCallbacks
    def test_icontains(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__icontains='oh').select()

    @defer.inlineCallbacks
    def test_startswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__startswith = "J").select()

    @defer.inlineCallbacks
    def test_istartswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__istartswith = "J").select()

    @defer.inlineCallbacks
    def test_endswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__endswith = "n").select()

    @defer.inlineCallbacks
    def test_iendswith(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(name__iendswith = "n").select()

    @defer.inlineCallbacks
    def test_range(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id__range = (0, 20)).select()

    @defer.inlineCallbacks
    def test_isnull(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__isnull = True).select()

    @defer.inlineCallbacks
    def test_notisnull(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(date__isnull = False).select()


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
        defer.returnValue(FooBar)

    @defer.inlineCallbacks
    def test_filter_then_exclude(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id__range = (0, 20)).exclude(id=5).select()

    @defer.inlineCallbacks
    def test_exclude_then_filter(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.exclude(id=5).filter(id__range = (0, 20)).select()

    @defer.inlineCallbacks
    def test_filter_then_filter(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.filter(id=5).filter(id__range = (0, 20)).select()

    @defer.inlineCallbacks
    def test_exclude_then_exclude(self):
        FooBar = yield self.setUpModel()
        results = yield FooBar.objects.exclude(id=5).exclude(id__range = (0, 20)).select()

