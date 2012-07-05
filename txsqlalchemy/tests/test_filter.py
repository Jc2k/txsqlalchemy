
from twisted.trial.unittest import TestCase
from twisted.internet import defer
from txsqlalchemy import Column, String, Integer, model_base

class TestFiltering(TestCase):

    def setUp(self):
        Base = model_base()
        class FooBar(Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            date = Column(String)
        self.Model = FooBar

    def test_simple(self):
        self.Model.objects.filter(name = "John")

    def test_exact(self):
        self.Model.objects.filter(name__exact="John")

    def test_day(self):
        self.Model.objects.filter(date__day = 5)

    def test_month(self):
        self.Model.objects.filter(date__month = 5)

    def test_year(self):
        self.Model.objects.filter(date__year = 2005)

    def test_week_date(self):
        self.Model.objects.filter(date__week_date = 5)

    def test_in(self):
        self.Model.objects.filter(name__in=(1,2,3))

    def test_contains(self):
        self.Model.objects.filter(name__contains='oh')

    def test_icontains(self):
        self.Model.objects.filter(name__icontains='oh')

    def test_startswith(self):
        self.Model.objects.filter(name__startswith = "J")

    def test_istartswith(self):
        self.Model.objects.filter(name__istartswith = "J")

    def test_endswith(self):
        self.Model.objects.filter(name__endswith = "n")

    def test_iendswith(self):
        self.Model.objects.filter(name__iendswith = "n")

    def test_range(self):
        self.Model.objects.filter(id__range = (0, 20))

    def test_isnull(self):
        self.Model.objects.filter(date__isnull = True)

    def test_notisnull(self):
        self.Model.objects.filter(date__isnull = False)


class TestChain(TestCase):

    def setUp(self):
        Base = model_base()
        class FooBar(Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            date = Column(String)
        self.Model = FooBar

    def test_filter_then_exclude(self):
        self.Model.objects.filter(id__range = (0, 20)).exclude(id=5)

    def test_exclude_then_filter(self):
        self.Model.objects.exclude(id=5).filter(id__range = (0, 20))

    def test_filter_then_filter(self):
        self.Model.objects.filter(id=5).filter(id__range = (0, 20))

    def test_exclude_then_exclude(self):
        self.Model.objects.exclude(id=5).exclude(id__range = (0, 20))

