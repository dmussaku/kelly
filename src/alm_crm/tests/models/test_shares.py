from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import (
    ContactFactory, 
    ShareFactory,
    HashTagFactory,
    HashTagReferenceFactory,
    )
from alm_crm.models import (
    Share,
    HashTag,
    HashTagReference,
    )

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

    def test_search_by_hashtags(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(
            company_id=self.company.id, owner_id=account2.user.id)

        for i in range(100):
            share = ShareFactory(
                company_id=self.company.id, 
                contact=contact, 
                share_from=account2.user, 
                share_to=self.user
                )
        shares = Share.objects.filter(company_id=self.company.id)
        for share in shares:
            hash_tag = HashTagFactory(
                text='#test')
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Share, 
                object_id=share.id, 
                company_id=self.company.id, 
                save=True)
        shares = Share.search_by_hashtags(
            company_id=self.company.id, search_query='#test')
        self.assertEqual(shares.count, 100)

        for share in shares[0:30]:
            hash_tag = HashTagFactory(
                text='#test2')
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Share, 
                object_id=share.id, 
                company_id=self.company.id, 
                save=True)
        shares = Share.search_by_hashtags(
            company_id=self.company.id, search_query='#test, #test2')
        self.assertEqual(shares.count, 30)
