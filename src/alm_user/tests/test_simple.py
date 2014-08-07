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


def extract_sessionid(cookies):
    for cookie_obj in cookies:
        if cookie_obj.get('name') == settings.SESSION_COOKIE_NAME:
            return cookie_obj.get('value')
    return None


with such.A('Alma.net accessibility') as it:
    it.uses(MainSeleniumLayer)

    @it.has_setup
    def setup():
        it.app_url = settings.SITE_DOMAIN
        MainSeleniumLayer.share_vars(it)

    @it.should('Show login page')
    def test():
        it.driver.get(it.app_url)
        it.assertIn('login page', it.driver.title.lower())

    with it.having('User entered incorrect password'):

        @it.has_setup
        def setup():
            it.login_url = it.app_url + reverse('user_login')
            it.current_user = create_test_user()
                # login
            it.driver.get(it.login_url)
            elem = it.driver.find_element_by_name('username')
            elem.send_keys(it.current_user.email)

            elem = it.driver.find_element_by_name('password')
            elem.send_keys('qweqwe')
            it.driver.find_element_by_id('id_submit').click()

        @it.should('incorrect password')
        def test():
            it.driver.find_element_by_class_name("errorlist")
            it.assertIn('login page', it.driver.title.lower())

    with it.having('User has session'):

        @it.has_setup
        def setup():
            it.login_url = it.app_url + reverse('user_login')
            #it.current_user = create_test_user()
            # login
            it.driver.get(it.login_url)
            elem = it.driver.find_element_by_name('username')
            elem.send_keys(it.current_user.email)

            elem = it.driver.find_element_by_name('password')
            elem.send_keys('123')

            it.driver.find_element_by_id('id_submit').click()

        @it.should('Redirect to profile page')
        def test():
            #it.driver.get(it.app_url)
            it.assertIn('profile', it.driver.title.lower())

    with it.having('User change settings'):

        @it.has_setup
        def setup():
            it.login_url = it.app_url + '/auth/profile/'

            # login
            it.driver.get(it.login_url)

            #it.driver.find_element_by_id('settings').click()

        @it.should('show page #Edit settings')
        def test():
            #it.driver.get(it.app_url)
            it.assertIn('change user settings', it.driver.title.lower())
            it.driver.find_element_by_name("profile-page-form")

    with it.having('User log out'):

        @it.has_setup
        def setup():
            it.login_url = it.app_url + reverse('user_list')
            it.driver.get(it.login_url)
            it.old_cookie = extract_sessionid(it.driver.get_cookies())
            it.driver.find_element_by_id('logout').click()

        @it.should('Redirect to profile page')
        def test():
            #it.driver.get(it.app_url)
            auth_val, auth_key = None, settings.SESSION_COOKIE_NAME
            it.assertIn('login page', it.driver.title.lower())

        @it.should('Have different session value or empty')
        def test_session():
            new_cookie = extract_sessionid(it.driver.get_cookies())
            it.assertNotEqual(it.old_cookie, new_cookie)
            it.assertTrue(not new_cookie is None)
"""
1. when user is logged in with incorrect password,
he must stay on the same page with error: "password incorrect".

2. when user is logged in with correct login and password
he must be redirected to profile page

3. when user is logged in and user enters "change settings"
he must be on the page titled "change user settings" and this page
should have form named "profile-page-form"

4. when user is logged in and he clicks on "log out" he must loose session,
and redirected to login page
"""
# with such.A('Alma.net authentication'):


it.createTests(globals())


class SimpleTestCase(TestCase):

    def test_user(self):
        u = User()
        u.first_name = "k"
        u.set_password('123')
        self.assertEqual(u.email, '')
        self.assertEqual(u.say_hi(), 'hi')
        self.assertTrue(u.check_password('123'))


