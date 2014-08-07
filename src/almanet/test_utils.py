from django.conf import settings
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver


class MainSeleniumLayer(object):

    driver = None
    shared_vars = None

    @classmethod
    def setUp(cls):
        path = '%s:%s/wd/hub' % (
            settings.SELENIUM_TESTSERVER_HOST,
            settings.SELENIUM_TESTSERVER_PORT)
        caps = getattr(DesiredCapabilities,
                       settings.SELENIUM_CAPABILITY,
                       DesiredCapabilities.CHROME)
        cls.shared_vars = dict()
        cls.shared_vars['driver'] = cls.driver = webdriver.Remote(
            command_executor=path,
            desired_capabilities=caps)

    @classmethod
    def tearDown(cls):
        cls.driver.close()
        del cls.driver

    @classmethod
    def share_vars(self, scenario):
        for k, v in self.shared_vars.items():
            setattr(scenario, k, v)
