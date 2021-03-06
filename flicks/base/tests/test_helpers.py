from datetime import datetime

from nose.tools import eq_

from flicks.base.helpers import babel_date, babel_number
from flicks.base.tests import TestCase


class TestHelpers(TestCase):
    def test_babel_date(self):
        date = datetime(2011, 9, 23)
        with self.activate('en-US'):
            eq_(babel_date(date, 'short'), '9/23/11')
            eq_(babel_date(date, 'medium'), 'Sep 23, 2011')

        with self.activate('fr'):
            eq_(babel_date(date, 'short'), '23/09/11')
            eq_(babel_date(date, 'medium'), '23 sept. 2011')

    def test_babel_number(self):
        number = 1000000
        with self.activate('en-US'):
            eq_(babel_number(number), u'1,000,000')

        with self.activate('fr'):
            # \xa0 is a non-breaking space
            eq_(babel_number(number), u'1\xa0000\xa0000')
