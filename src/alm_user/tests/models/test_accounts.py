from django.test import TestCase

from alm_crm.tests.models import TestMixin
from alm_crm.factories import ContactFactory

class UserTestCase(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_follow_unfollow(self):
    	c = ContactFactory(company_id=self.company.id, owner_id=self.user.id)
    	self.assertEqual(self.account.unfollow_list.count(), 0)

    	self.account.follow_unfollow(contact_ids=[c.id])
    	self.assertEqual(self.account.unfollow_list.count(), 1)

    	self.account.follow_unfollow(contact_ids=[c.id])
    	self.assertEqual(self.account.unfollow_list.count(), 0)