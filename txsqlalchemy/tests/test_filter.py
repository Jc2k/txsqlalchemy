
from twisted.internet import defer
from txsqlalchemy import Column, DateTime, String, Integer, model_base
import datetime

from .base import FixtureTestCase, fixtures

class TestFiltering(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_simple(self):
        results = yield self.FooBar.objects.filter(name = "John")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_multiple_column_types(self):
        results = yield self.FooBar.objects.filter(name="John")
        self.assertEqual(isinstance(results[0].id, int), True)
        self.assertEqual(isinstance(results[0].name, basestring), True)
        self.assertEqual(isinstance(results[0].date, datetime.datetime), True)

    @defer.inlineCallbacks
    def test_exact(self):
        results = yield self.FooBar.objects.filter(name__exact="John")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_day(self):
        results = yield self.FooBar.objects.filter(date__day = 5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Peter")

    @defer.inlineCallbacks
    def test_month(self):
        results = yield self.FooBar.objects.filter(date__month = 5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Timothy")

    @defer.inlineCallbacks
    def test_year(self):
        results = yield self.FooBar.objects.filter(date__year = 2005)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_week_date(self):
        results = yield self.FooBar.objects.filter(date__week_date = 5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_in(self):
        results = yield self.FooBar.objects.filter(id__in=(1,2,3))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")
        self.assertEqual(results[2].name, "Timothy")

    @defer.inlineCallbacks
    def test_contains(self):
        results = yield self.FooBar.objects.filter(name__contains='oh')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    #@defer.inlineCallbacks
    #def test_contains_is_case_sensitive(self):
    #    results = yield self.FooBar.objects.filter(name__contains='OH')
    #    self.assertEqual(len(results), 0)

    @defer.inlineCallbacks
    def test_icontains(self):
        results = yield self.FooBar.objects.filter(name__icontains='OH')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_startswith(self):
        results = yield self.FooBar.objects.filter(name__startswith = "J")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_istartswith(self):
        results = yield self.FooBar.objects.filter(name__istartswith = "j")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_endswith(self):
        results = yield self.FooBar.objects.filter(name__endswith = "n")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_iendswith(self):
        results = yield self.FooBar.objects.filter(name__iendswith = "N")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_range(self):
        results = yield self.FooBar.objects.filter(id__range = (0, 20))
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")
        self.assertEqual(results[2].name, "Timothy")
        self.assertEqual(results[3].name, "Peter")

    @defer.inlineCallbacks
    def test_isnull(self):
        results = yield self.FooBar.objects.filter(date__isnull = True)
        self.assertEquals(len(results), 0)

    @defer.inlineCallbacks
    def test_notisnull(self):
        results = yield self.FooBar.objects.filter(date__isnull = False)
        self.assertEquals(len(results), 4)


class TestChain(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_filter_then_exclude(self):
        results = yield self.FooBar.objects.filter(id__range = (0, 20)).exclude(id=2)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "John")

    @defer.inlineCallbacks
    def test_exclude_then_filter(self):
        results = yield self.FooBar.objects.exclude(id=1).filter(id__range = (0, 20))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_filter_then_filter(self):
        results = yield self.FooBar.objects.filter(id=2).filter(id__range = (0, 20))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alex")

    @defer.inlineCallbacks
    def test_exclude_then_exclude(self):
        results = yield self.FooBar.objects.exclude(id=1).exclude(id__range = (0, 20))
        self.assertEqual(len(results), 0)


class TestSlice(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_start_no_stop(self):
        results = yield self.FooBar.objects[1:]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Alex")
        self.assertEqual(results[1].name, "Timothy")
        self.assertEqual(results[2].name, "Peter")

    @defer.inlineCallbacks
    def test_no_start_stop(self):
        results = yield self.FooBar.objects[:2]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].name, "John")
        self.assertEqual(results[1].name, "Alex")

    @defer.inlineCallbacks
    def test_no_start_no_stop(self):
        results = yield self.FooBar.objects[2:2]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].name, "Timothy")
        self.assertEqual(results[1].name, "Peter")


class TestCount(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_case(self):
        count = yield self.FooBar.objects.count()
        self.assertEquals(count, 4)


class TestGet(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    def test_multiple_objects(self):
        d = self.FooBar.objects.get(name__contains = "o")
        self.assertFailure(d, self.FooBar.MultipleObjectsReturned)

    def test_does_not_exist(self):
        d = self.FooBar.objects.get(name = "Doug")
        self.assertFailure(d, self.FooBar.DoesNotExist)

    @defer.inlineCallbacks
    def test_single_object_returned(self):
        peter = yield self.FooBar.objects.get(name = "Peter")
        self.assertEqual(peter.name, "Peter")


class TestOrdering(FixtureTestCase):

    __fixture__ = fixtures.FooBarBaz

    @defer.inlineCallbacks
    def test_order_ascending(self):
        rows = yield self.FooBar.objects.all().order_by("name")
        self.assertEqual(rows[0].name, "Alex")
        self.assertEqual(rows[1].name, "John")
        self.assertEqual(rows[2].name, "Peter")
        self.assertEqual(rows[3].name, "Timothy")

    @defer.inlineCallbacks
    def test_order_descending(self):
        rows = yield self.FooBar.objects.all().order_by("-name")
        self.assertEqual(rows[0].name, "Timothy")
        self.assertEqual(rows[1].name, "Peter")
        self.assertEqual(rows[2].name, "John")
        self.assertEqual(rows[3].name, "Alex")

