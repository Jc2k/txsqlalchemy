from twisted.internet import defer
from .base import Fixture

from txsqlalchemy import Column, Integer, String, ForeignKey


class Cocktails(Fixture):

    @defer.inlineCallbacks
    def setUp(self, testcase):
        super(Cocktails, self).setUp(testcase)

        class Drink(self.Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
        yield Drink.create()
        yield Drink.insert(name = "Long Island Ice Tea")
        testcase.Drink = self.Drink = Drink

        class Ingredient(self.Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
            drink = ForeignKey("drink.id")
        yield Ingredient.create()
        testcase.Ingredient = self.Ingredient = Ingredient

        class Measure(self.Base):
            id = Column(Integer, primary_key=True)
            size = Column(Integer)
            drink = ForeignKey("drink.id")
            ingredient = ForeignKey("ingredient.id")
        yield Measure.create()
        testcase.Measure = self.Measure = Measure

