from django.test import TestCase
from django.contrib.auth import authenticate

from alm_crm.tests.models import TestMixin

class UserTestCase(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_auth(self):
    	u = authenticate(
    		username=self.user.email,
    		password='123'
    		)
    	self.assertEqual(u, self.user)