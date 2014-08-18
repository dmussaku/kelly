from nose2.plugins.loader.functions import Functions as Nose2Functions
from nose2.compat import unittest
from nose2 import util
from django.utils.module_loading import import_by_path
from django.test.testcases import LiveServerTestCase
from django.conf import settings


class SeleniumLiveTestCase(LiveServerTestCase, unittest.FunctionTestCase):
    pass


class Functions(Nose2Functions):
    test_case_class = None
    configSection = 'functions-ext'

    def __init__(self, *a, **kw):
        test_case = self.config.as_str('test_case')
        self.test_case_class = self.load_test_case_or_default(
            test_case, default=unittest.FunctionTestCase)

    def load_test_case_or_default(self, test_case_pypath, default=None):
        try:
            return import_by_path(test_case_pypath)
        except:
            if default:
                return default
        return None

    def _createTests(self, obj):
        if not hasattr(obj, 'setUp'):
            if hasattr(obj, 'setup'):
                obj.setUp = obj.setup
            elif hasattr(obj, 'setUpFunc'):
                obj.setUp = obj.setUpFunc
        if not hasattr(obj, 'tearDown'):
            if hasattr(obj, 'teardown'):
                obj.tearDown = obj.teardown
            elif hasattr(obj, 'tearDownFunc'):
                obj.tearDown = obj.tearDownFunc

        tests = []
        args = {}
        setUp = getattr(obj, 'setUp', None)
        tearDown = getattr(obj, 'tearDown', None)
        if setUp is not None:
            args['setUp'] = setUp
        if tearDown is not None:
            args['tearDown'] = tearDown

        paramList = getattr(obj, 'paramList', None)
        isGenerator = util.isgenerator(obj)
        if paramList is not None or isGenerator:
            return tests
        else:
            case = util.transplant_class(
                self.test_case_class, obj.__module__)(obj, **args)
            tests.append(case)
        return tests
