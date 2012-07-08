
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from txsqlalchemy import Column, Integer, String, ForeignKey, model_base

class TestRelationships(TestCase):

    @defer.inlineCallbacks
    def setUp(self):
        Base = model_base()
        Base.bind("sqlite://")

        class Drink(Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
        yield Drink.create()
        yield Drink.insert(name = "Long Island Ice Tea")
        self.Drink = Drink

        class Ingredient(Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            drink = ForeignKey("drink.id")
        yield Ingredient.create()
        self.Ingredient = Ingredient

    @defer.inlineCallbacks
    def test_children_all(self):
        drinks = yield self.Drink.objects.all().select()
        drink = drinks[0]
        #ingredients = yield drink.ingredients.all()


class TestSave(TestCase):

    @defer.inlineCallbacks
    def setUp(self):
        Base = model_base()
        Base.bind("sqlite://")
        class Foo(Base):
            a = Column(String)
        yield Foo.create()
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

        results = yield self.Model.objects.all().select()
        self.assertEqual(results[0].a, '1')

    @defer.inlineCallbacks
    def test_save_then_update(self):
        foo = self.Model()
        foo.a = '1'
        yield foo.save()

        results = yield self.Model.objects.all().select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].a, '1')

        results[0].a = '234'
        yield results[0].save()

        results = yield self.Model.objects.all().select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].a, '234')



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


class TestInsert(TestCase):

    @defer.inlineCallbacks
    def test_insert_row(self):
        Base = model_base()
        Base.bind("sqlite://")
        class Foo(Base):
            abx = Column(String)
        yield Foo.create()

        results = yield Foo.objects.all().select()
        self.assertEqual(len(results), 0)

        yield Foo.insert(abx="1")
        results = yield Foo.objects.all().select()
        self.assertEqual(len(results), 1)
        
        yield Foo.insert(abx="33")
        results = yield Foo.objects.all().select()
        self.assertEqual(len(results), 2)
 
