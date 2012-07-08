from twisted.trial.unittest import TestCase

from . import fixtures


class FixtureTestCase(TestCase):

    __fixture__ = None

    def setUp(self):
        self.fixture = self.__fixture__()
        return self.fixture.setUp(self)

 
