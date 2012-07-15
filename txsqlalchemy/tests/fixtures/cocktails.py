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
        testcase.Drink = self.Drink = Drink

        drink = yield Drink.insert(name = "Long Island Ice Tea")


        class Ingredient(self.Base):
            id = Column(Integer, primary_key=True)
            name = Column(String)
        yield Ingredient.create()
        testcase.Ingredient = self.Ingredient = Ingredient

        rum = yield Ingredient.insert(name = "Rum")
        vodka = yield Ingredient.insert(name = "Vodka")
        triplesec = yield Ingredient.insert(name = "Triplesec")
        gin = yield Ingredient.insert(name = "Gin")
        tequila = yield Ingredient.insert(name = "Tequila")


        class Measure(self.Base):
            id = Column(Integer, primary_key=True)
            size = Column(Integer)
            drink = ForeignKey("drink.id")
            ingredient = ForeignKey("ingredient.id")
        yield Measure.create()
        testcase.Measure = self.Measure = Measure

        yield Measure.insert(drink=drink, ingredient=rum, size=1)
        yield Measure.insert(drink=drink, ingredient=vodka, size=1)
        yield Measure.insert(drink=drink, ingredient=triplesec, size=1)
        yield Measure.insert(drink=drink, ingredient=gin, size=1)
        yield Measure.insert(drink=drink, ingredient=tequila, size=1)

