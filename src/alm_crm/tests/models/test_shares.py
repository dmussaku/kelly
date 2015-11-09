from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import ContactFactory, ShareFactory
from alm_crm.models import Share

from . import TestMixin


class ShareTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_get_by_user(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id, owner_id=account2.user.id)

        for i in range(3):
            share = ShareFactory(company_id=self.company.id, contact=contact, share_from=account2.user, share_to=self.user)
        
        shares = Share.get_by_user(company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(shares['shares'].count(), 3)

    def test_mark_as_read(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id, owner_id=account2.user.id)

        shares = []

        for i in range(3):
            share = ShareFactory(company_id=self.company.id, contact=contact, share_from=account2.user, share_to=self.user)
            shares.append(share.id)
        
        shares = Share.mark_as_read(company_id=self.company.id, user_id=self.user.id, ids=shares)
        shares = Share.get_by_user(company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(shares['shares'].count(), 3)
        self.assertEqual(shares['not_read'], 0)
