from nose2.tools import such
from almanet.test_utils import MainSeleniumLayer
from alm_user.models import User
from alm_utils import pj
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from alm_user.models import User


def create_test_user():
    u = User()
    u.first_name = 'Rustem'
    u.last_name = 'Kamun'
    u.email = 'r.kamun@gmail.com'
    u.save()
    u.set_password('123')

    return u


with such.A('Alma.net accessibility') as it:
    it.uses(MainSeleniumLayer)

    @it.has_setup
    def setup():
        it.app_url = settings.SITE_DOMAIN
        MainSeleniumLayer.share_vars(it)

    @it.should('Show login page')
    def test():
        it.driver.get(it.app_url)
        it.assertIn('login', it.driver.title.lower())

    with it.having('User has session'):


        @it.has_setup
        def setup():
            it.login_url = it.app_url + reverse('user_login')
            it.current_user = create_test_user()
            # login
            it.driver.get(it.login_url)
            elem = it.driver.find_element_by_name('username')
            elem.send_keys(it.current_user.email)

            elem = it.driver.find_element_by_name('password')
            elem.send_keys('123')

            it.driver.find_element_by_id('id_submit').click()

        @it.should('Redirect to profile page')
        def test():
            it.driver.get(it.app_url)
            it.assertIn('profile', it.driver.title.lower())


it.createTests(globals())


class SimpleTestCase(TestCase):

    def test_user(self):
        u = User()
        u.first_name = "k"
        u.set_password('123')
        self.assertEqual(u.email, '')
        self.assertEqual(u.say_hi(), 'hi')
        self.assertTrue(u.check_password('123'))


