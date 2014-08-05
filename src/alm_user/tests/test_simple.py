from nose2.tools import such
from alm_user.models import User
from django.test import TestCase
from django.conf import settings
# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

print settings.SELENIUM_TESTSERVER_HOST


class AlmaUserLayer(object):
    description = '*** Auth System layer ***'

    @classmethod
    def setUp(cls):
        it.url = 'http://bb.co.uk/user/signin'
        it.email = "r.kamun@gmail.com"
        #driver = webdriver.Firefox()
        # it.driver = webdriver.Remote(
        #     command_executor='http://192.168.233.1:4444/wd/hub',
        #     desired_capabilities=DesiredCapabilities.FIREFOX)

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

    # @it.should('ask a google')
    # def test_selenium():
    #     it.driver.get("http://www.google.com")
    #     it.assertIn("Google", it.driver.title)


it.createTests(globals())


class SimpleTestCase(TestCase):

    def test_user(self):
        u = User()
        u.first_name = "k"
        u.set_password('123')
        self.assertEqual(u.email, '')
        self.assertEqual(u.say_hi(), 'hi')
        self.assertTrue(u.check_password('123'))


