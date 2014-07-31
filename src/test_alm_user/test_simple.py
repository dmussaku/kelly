from nose2.tools import such, params
from alm_user.models import User
from django.test import TestCase


class AlmaUserLayer(object):
    description = '*** Auth System layer ***'

    @classmethod
    def setUp(cls):
        it.url = 'http://bb.co.uk/user/signin'
        it.email = "r.kamun@gmail.com"

    @classmethod
    def tearDown(cls):
        del it.url
        del it.email

with such.A('Global auth system') as it:

    it.uses(AlmaUserLayer)

    @it.has_setup
    def setup():
        pass

    @it.has_teardown
    def teardown():
        pass

    @it.should('say hi')
    def test():
        it.assertEqual(it.email, 'r.kamun@gmail.com')


it.createTests(globals())


class SimpleTestCase(TestCase):

    def test_user(self):
        u = User(last_name='Kamun')
        self.assertEqual(u.email, '')


