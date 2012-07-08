
from twisted.internet import defer
from txsqlalchemy import Column, DateTime, String, Integer, model_base
import datetime

from .base import FixtureTestCase, fixtures

class TestFiltering(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_simple(self):
        results = yield self.FooBar.objects.filter(name = "John").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_exact(self):
        results = yield self.FooBar.objects.filter(name__exact="John").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_day(self):
        results = yield self.FooBar.objects.filter(date__day = 5).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Peter")

    @defer.inlineCallbacks
    def test_month(self):
        results = yield self.FooBar.objects.filter(date__month = 5).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Timothy")

    @defer.inlineCallbacks
    def test_year(self):
        results = yield self.FooBar.objects.filter(date__year = 2005).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_week_date(self):
        results = yield self.FooBar.objects.filter(date__week_date = 5).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_in(self):
        results = yield self.FooBar.objects.filter(id__in=(1,2,3)).select()
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")
        self.assertEqual(results[2].name, "Timothy")

    @defer.inlineCallbacks
    def test_contains(self):
        results = yield self.FooBar.objects.filter(name__contains='oh').select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    #@defer.inlineCallbacks
    #def test_contains_is_case_sensitive(self):
    #    results = yield self.FooBar.objects.filter(name__contains='OH').select()
    #    self.assertEqual(len(results), 0)

    @defer.inlineCallbacks
    def test_icontains(self):
        results = yield self.FooBar.objects.filter(name__icontains='OH').select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_startswith(self):
        results = yield self.FooBar.objects.filter(name__startswith = "J").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_istartswith(self):
        results = yield self.FooBar.objects.filter(name__istartswith = "j").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_endswith(self):
        results = yield self.FooBar.objects.filter(name__endswith = "n").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_iendswith(self):
        results = yield self.FooBar.objects.filter(name__iendswith = "N").select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_range(self):
        results = yield self.FooBar.objects.filter(id__range = (0, 20)).select()
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")
        self.assertEqual(results[2].name, "Timothy")
        self.assertEqual(results[3].name, "Peter")

    @defer.inlineCallbacks
    def test_isnull(self):
        results = yield self.FooBar.objects.filter(date__isnull = True).select()
        self.assertEquals(len(results), 0)

    @defer.inlineCallbacks
    def test_notisnull(self):
        results = yield self.FooBar.objects.filter(date__isnull = False).select()
        self.assertEquals(len(results), 4)


class TestChain(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_filter_then_exclude(self):
        results = yield self.FooBar.objects.filter(id__range = (0, 20)).exclude(id=2).select()
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_exclude_then_filter(self):
        results = yield self.FooBar.objects.exclude(id=1).filter(id__range = (0, 20)).select()
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_filter_then_filter(self):
        results = yield self.FooBar.objects.filter(id=2).filter(id__range = (0, 20)).select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_exclude_then_exclude(self):
        results = yield self.FooBar.objects.exclude(id=1).exclude(id__range = (0, 20)).select()
        self.assertEqual(len(results), 0)


class TestCount(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_case(self):
        count = yield self.FooBar.objects.count()
        self.assertEquals(count, 4)


