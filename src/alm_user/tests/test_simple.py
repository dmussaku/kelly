# from mock import MagicMock
# from nose2.tools import such
# from almanet.test_utils import MainSeleniumLayer
# from alm_user.models import User
# from django.conf import settings
# from django.core.urlresolvers import reverse

# TEST_EMAIL = 'asdasd@mail.ru'


# def test_user():
#     u = MagicMock()
#     u.first_name = 'Rustem'
#     u.last_name = 'Kamun'
#     u.email = TEST_EMAIL
#     u.password = '123'
#     u.company = 'almacloud'

#     return u


# def create_test_user():
#     u = User()
#     u.first_name = 'Rustem'
#     u.last_name = 'Kamun'
#     u.email = TEST_EMAIL
#     u.save()
#     u.set_password('123')

#     return u


# def delete_test_user(user):
#     u = User.objects.get(email=user.email)
#     u.delete()


# def create_inactive_test_user():
#     u = User()
#     u.first_name = 'Yernar'
#     u.last_name = 'Mailubai'
#     u.email = 'mailubai@mail.com'
#     u.is_active = False
#     u.save()
#     u.set_password('qwe')

#     return u


# def extract_sessionid(cookies):
#     for cookie_obj in cookies:
#         if cookie_obj.get('name') == settings.SESSION_COOKIE_NAME:
#             return cookie_obj.get('value')
#     return None


# with such.A('Alma.net accessibility') as it:
#     it.uses(MainSeleniumLayer)

#     @it.has_setup
#     def setup():
#         it.app_url = settings.SITE_DOMAIN
#         MainSeleniumLayer.share_vars(it)

#     @it.should('Show login page')
#     def test():
#         it.driver.get(it.app_url)
#         it.assertIn('login page', it.driver.title.lower())

# with such.A('Alma.net Registration') as it:
#     it.uses(MainSeleniumLayer)

#     @it.has_setup
#     def setup():
#         it.app_url = settings.SITE_DOMAIN
#         MainSeleniumLayer.share_vars(it)
#         it.current_user = test_user()

#         it.registration_url = it.app_url + reverse('user_registration')

#         it.driver.get(it.registration_url)
#         elem = it.driver.find_element_by_name('first_name')
#         elem.send_keys(it.current_user.first_name)

#         elem = it.driver.find_element_by_name('last_name')
#         elem.send_keys(it.current_user.last_name)

#         elem = it.driver.find_element_by_name('email')
#         elem.send_keys(it.current_user.email)

#         elem = it.driver.find_element_by_name('password')
#         elem.send_keys(it.current_user.password)

#         elem = it.driver.find_element_by_name('confirm_password')
#         elem.send_keys(it.current_user.password)

#         elem = it.driver.find_element_by_name('company_name')
#         elem.send_keys(it.current_user.company)

#         it.driver.find_element_by_xpath("//input[@type='submit']").click()

#     @it.has_teardown
#     def teardown():
#         User.objects.filter(email=TEST_EMAIL).delete()


#     @it.should('Complete registration')
#     def test():
#         it.assertIn('login page', it.driver.title.lower())

#     # case 4.a. TEST 2
#     with it.having('User sign in: Incorrect email'):

#         @it.has_setup
#         def setup():
#             # Steps 1.2.3. are part of setup. 4 a.b.c.d. and 5 is what to be tested
#             # Setting up 1.
#             it.login_url = it.app_url + reverse('user_login')
#             # it.current_user = create_test_user()
#             it.driver.get(it.login_url)
#             # locate username field
#             elem = it.driver.find_element_by_name('username')
#             # send the fake username info
#             fake_email = "fake_sherlock@holmes.me"
#             elem.send_keys(fake_email)
#             # locate the password field
#             elem = it.driver.find_element_by_name('password')
#             # enter the correct password                ??? DIFFERENT TEST CASE
#             # FOR INCORRECT PASSWORD
#             elem.send_keys("123")
#             # click submit
#             it.driver.find_element_by_id('id_submit').click()

#         @it.should('report user with such email does not exist')
#         def test():
#             # find list of errors
#             it.driver.find_element_by_class_name('errorlist')
#             # assert that incorrect email error is in the errorlist
#             it.assertIn('login page', it.driver.title.lower())

#         @it.has_teardown
#         def teardown():
#             User.objects.get(email=TEST_EMAIL).delete()


#     # case 4.b.  TEST 3
#     # this case was handled in 1, see above
#     with it.having('User enters incorrect password'):

#         @it.has_setup
#         def setup():
#             it.login_url = it.app_url + reverse('user_login')
#             it.current_user = create_test_user()
#             # login
#             it.driver.get(it.login_url)
#             elem = it.driver.find_element_by_name('username')
#             elem.send_keys(it.current_user.email)

#             elem = it.driver.find_element_by_name('password')
#             elem.send_keys('qweqwe')
#             it.driver.find_element_by_id('id_submit').click()

#         @it.has_teardown
#         def teardown():
#             User.objects.filter(email=TEST_EMAIL).delete()

#         @it.should('incorrect password')
#         def test():
#             it.driver.find_element_by_class_name("errorlist")

#         @it.should('stay on login page')
#         def test():
#             it.assertIn('login page', it.driver.title.lower())

#     # case 4.c. TEST 4
#     # if user has not activated their profile, they should stay on login page
#     # after submitting form
#     with it.having('User has not activated their account'):

#         @it.has_setup
#         def setup():
#             it.login_url = it.app_url + reverse('user_login')
#             it.current_user = create_inactive_test_user()
#             # locate username field
#             elem = it.driver.find_element_by_name('username')
#             # send the correct username info
#             elem.send_keys(it.current_user.email)
#             # locate password field
#             elem = it.driver.find_element_by_name('password')
#             # send the correct password info
#             elem.send_keys("qwe")
#             # click submit
#             it.driver.find_element_by_id('id_submit').click()

#         @it.should('report user is inactive')
#         def test():
#             # assert that inactive user stays on login page
#             it.assertIn('login page', it.driver.title.lower())
#             # delete inactive user

#         @it.has_teardown
#         def teardown():
#             User.objects.filter(email=TEST_EMAIL).delete()

#     # case 4.d. TEST 5
#     with it.having('User activate user session'):

#         @it.has_setup
#         def setup():
#             it.login_url = it.app_url + reverse('user_login')
#             it.current_user = create_test_user()
#             # locate username field
#             elem = it.driver.find_element_by_name('username')
#             # send the correct username info
#             elem.send_keys(it.current_user.email)
#             # locate password field
#             elem = it.driver.find_element_by_name('password')
#             # send the correct password info
#             elem.send_keys("123")
#             # click submit
#             it.driver.find_element_by_id('id_submit').click()

#         @it.should('user has session id')
#         def test():
#             # extract the cookie to see it it's none
#             it.cookie = extract_sessionid(it.driver.get_cookies())
#             # fail if it's NONE
#             it.assertIsNotNone(it.cookie)


#         @it.has_teardown
#         def teardown():
#             User.objects.filter(email=TEST_EMAIL).delete()

#     # 2 TEST 7
#     with it.having('session'):

#         @it.has_setup
#         def setup():
#             it.login_url = it.app_url + reverse('user_login')
#             it.current_user = create_test_user()
#             # login
#             it.driver.get(it.login_url)
#             # find the field and fill it in
#             elem = it.driver.find_element_by_name('username')
#             elem.send_keys(it.current_user.email)
#             # find the field and fill it in
#             elem = it.driver.find_element_by_name('password')
#             elem.send_keys('123')
#             # click on submit button
#             it.driver.find_element_by_id('id_submit').click()

#         @it.should('Redirect to profile page')
#         def test():
#             # assert that user profile was opened
#             it.assertIn('user profile', it.driver.title.lower())

#         @it.has_teardown
#         def teardown():
#             User.objects.filter(email=TEST_EMAIL).delete()

#     # 3 TEST 8
#     with it.having('User change settings'):

#         @it.has_setup
#         def setup():
#             # as we're logged in, click on Settings href
#             it.driver.find_element_by_link_text('Settings').click()

#         @it.should('show page Edit settings')
#         def test():
#             # assert that we're in settings change page
#             it.assertIn('user profile settings page', it.driver.title.lower())
#             # THIS TEST MAY NOT BE THOROUGH

#     # 4 TEST 9
#     with it.having('User log out'):

#         @it.has_setup
#         def setup():
#             it.old_cookie = extract_sessionid(it.driver.get_cookies())
#             it.driver.find_element_by_id('logout').click()

#         @it.should('Redirect to login page')
#         def test():
#             it.assertIn('login page', it.driver.title.lower())

#         @it.should('Have different session value or empty')
#         def test_session():
#             new_cookie = extract_sessionid(it.driver.get_cookies())
#             it.assertNotEqual(it.old_cookie, new_cookie)
#             it.assertTrue(not new_cookie is None)

#     # 5 TEST 10
#     with it.having('User password reset'):

#         @it.has_setup
#         def setup():
#             # get the right url
#             it.login_url = it.app_url + reverse('user_login')
#             # find reset password button
#             elem = it.driver.find_element_by_link_text("Reset your password")
#             # click it
#             elem.click()
#         # on click browser should redirect us to password resetting page

#         @it.should('contain h1 tag with password reset title')
#         def test():
#             # check if page contains h1 tag with 'password reset'
#             # get the h1 heading content and compare it against given text
#             xpath = '//h1'
#             elem = it.driver.find_element_by_xpath(xpath)
#             value = elem.text
#             it.assertIn('password reset', value.lower())

#         @it.should('redirect to password reset titled page')
#         def test():
#             # check the title page
#             it.assertIn('password reset', it.driver.title.lower())

#     # SECOND SET OF REQS
#     """
#     ADDED 14/08/2014

#     View user profile

#     Precondition: user has active session (he is logged in)

#     User opens profile page e.g. profile
#     User can preview profile page with his
#         Basic information: first_name, last_name
#         Preferences: timezone, language
#         Available Services (links to available services)
#         Billing information
#         Credit card details
#     """
#     # PREP TEST TO MAKE SURE WE'RE LOGGED IN
#     with it.having('logging in'):

#         @it.has_setup
#         def setup():
#             it.login_url = it.app_url + reverse('user_login')
#             it.current_user = test_user()
#             # login
#             it.driver.get(it.login_url)
#             # find the field and fill it in
#             elem = it.driver.find_element_by_name('username')
#             elem.send_keys(it.current_user.email)
#             # find the field and fill it in
#             elem = it.driver.find_element_by_name('password')
#             elem.send_keys('123')
#             # click on submit button
#             it.driver.find_element_by_id('id_submit').click()

#         @it.should('Redirect to profile page')
#         def test():
#             it.assertIn('user profile', it.driver.title.lower())

#         @it.should('have certain fields')
#         def test():
#             # fields to compare against
#             stack_of_fields = [
#                 "Company", "Country", "City", "Email", "Last name", "First name"]
#             # getting all elements using xpath
#             all_elements = it.driver.find_elements_by_css_selector('li')
#             # check against stack of specified fields
#             for elem in all_elements:
#                 field = stack_of_fields.pop()
#                 it.assertIn(field, elem.text)

#         @it.should('NOT have certain fields')
#         def test():
#             # fields to compare against
#             stack_of_fields = [
#                 "Fizz", "Buzz", "FizzBuzz", "Foo", "Bar", "FooBar"]
#             # getting all elements using xpath
#             all_elements = it.driver.find_elements_by_css_selector('li')
#             # check against stack of specified fields
#             for elem in all_elements:
#                 field = stack_of_fields.pop()
#                 it.assertNotEqual(field, elem.text)

#         @it.should('could view what time it is')
#         def test():
#             s = "Your time is:"
#             elem = it.driver.find_element_by_css_selector('p')
#             it.assertIn(s, elem.text)
#             # NOT SURE HOW TO TEST IF ACTUAL TIME IS DISPLAYED

#         @it.should('have a link to connected services')
#         def test():
#             s = "View connected services"
#             # find href with services text link
#             # this makes sure that it is a link bc we're using partial_link_text
#             # and it has the specified string
#             elem = it.driver.find_element_by_partial_link_text('services')
#             it.assertIn(s, elem.text)

#     # YET TO DO BILLING INFO AND CREDIT CARD INFO TESTS.
#     # TO BE DONE AFTER CLARIFYING EXACT REQS WITH YERNAR.

#     # THIRD SET OF REQS
#     """
#     Edit user profile
#         Precondition: user has active session (he is logged in)

#         1. User enters profile edit page e.g. profile/edit
#         2. User updates fields and submits
#         3. User redirected to profile e.g. profile
#         4. User notified with messages that he successfully updated profile
#     """
#     # AT THIS POINT WE'RE STILL LOGGED IN AFTER THE PREVIOUS TESTS
#     # RUN A PRETEST JUST TO MAKE SURE WE'RE LOGGED IN

#     with it.having('user is still logged in'):

#         @it.should('be in user profile page')
#         def test():
#             it.assertIn('user profile', it.driver.title.lower())

#     with it.having('clicked the settings link on profile page'):

#         @it.has_setup
#         def setup():
#             # go to the settings page. could be accomplished in 2 ways, just clicking settings or
#             # going to specific url that directs us to user settings page.
#             # Chose the first.
#             elem = it.driver.find_element_by_link_text('Settings')
#             elem.click()

#         @it.should('go to setttings page')
#         def test():
#             it.assertIn('user profile settings page', it.driver.title.lower())

#     # THIS TEST NEEDS TO BE WORKED ON
#     with it.having('being on the settings page'):

#         @it.has_setup
#         def setup():
#             first_name = "Yernar"
#             last_name = "Mailubai"
#             # changing name fields
#             elem = it.driver.find_element_by_name('first_name')
#             # clears out field from previous value, i.e. different first name
#             # to be changed
#             elem.clear()
#             elem.send_keys(first_name)
#             elem = it.driver.find_element_by_name('last_name')
#             # clears out field from previous value, i.e. different last name to
#             # be changed
#             elem.clear()
#             elem.send_keys(last_name)
#             # changing the timezone field

#             # find submit button
#             xpath = "//input[@type='submit']"
#             elem = it.driver.find_element_by_xpath(xpath)
#             elem.click()

#         @it.should('successfully fill out name fields and redirects to user profile')
#         def test():
#             # as soon as user updates fields and submits -- redirect to profile
#             # page
#             it.assertIn('user profile', it.driver.title.lower())

#         @it.should('should contain headline - notifies of successfully updated profile')
#         def test():
#             # find headline which contains message
#             elem = it.driver.find_elements_by_css_selector('h2')
#             message = "Your information was updated successfully"
#             it.assertEqual(message, elem.text)


# it.createTests(globals())
