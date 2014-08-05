from django.conf import settings
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class MainSeleniumLayer(object):

    @classmethod
    def setUp(cls):
        path = '%s:%s/wd/hub' % (
            settings.SELENIUM_TESTSERVER_HOST,
            settings.SELENIUM_TESTSERVER_PORT)
        caps = getattr(DesiredCapabilities,
                       settings.SELENIUM_CAPABILITY,
                       DesiredCapabilities.CHROME)
        it.driver = webdriver.Remote(
            command_executor=path,
            desired_capabilities=caps)

    @classmethod
    def tearDown(cls):
        it.driver.close()
        del it.driver
