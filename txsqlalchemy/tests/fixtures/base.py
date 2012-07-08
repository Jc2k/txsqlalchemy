from txsqlalchemy import model_base

class Fixture(object):

    def setUp(self, testcase):
        testcase.Base = self.Base = Base = model_base()
        Base.bind("sqlite://")

