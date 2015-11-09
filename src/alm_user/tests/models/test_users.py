import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import SalesCycleFactory, ContactFactory, ActivityFactory
from alm_crm.models import SalesCycle, Milestone

from alm_crm.tests.models import TestMixin

class UserTestCase(TestMixin, TestCase):
	def setUp(self):
        self.set_user()

    from django.contrib.auth import authenticate
    def test_auth(self):
    	print self.user.email
    	u = authenticate(
    		username=self.user.email,
    		password='123'
    		)
    	self.assertEqual(u, self.user)