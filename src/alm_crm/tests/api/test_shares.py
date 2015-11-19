import simplejson as json

from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.factories import ContactFactory, ShareFactory
from alm_crm.models import (
    Contact,
    Share,
    Contact,
    HashTag,
    HashTagReference,
)
from alm_crm.factories import ContactFactory, ShareFactory
from alm_crm.filters import ShareFilter

from . import APITestMixin

class ShareAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.shares_count = 5
        self.setUpShares(self.shares_count)

    def setUpShares(self, shares_count):
        contact = ContactFactory(company_id=self.company.id, owner_id=self.company.id)
        for i in range(shares_count):
            ShareFactory(company_id=self.company.id, share_from=self.user, share_to=self.user, contact=contact)

    def test_mark_as_read(self):
        """
        Ensure we can mark as read
        """
        url, parsed = self.prepare_urls('v1:share-read', subdomain=self.company.subdomain)
        
        response = self.client.post(url, [], HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, [], HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertTrue(content.has_key('count'))
        self.assertTrue(content.has_key('statistics'))

    def test_search_by_hashtags(self):
        company = self.company
        user = self.user

        for i in range(0,100):
            c = ContactFactory(owner=self.user, company_id=self.company.id)
            share = ShareFactory(
                contact=c,
                share_to=user,
                share_from=user,
                owner=user,
                company_id=company.id
                )
            hash_tag = HashTag(text='#test')
            hash_tag.save()
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Share, 
                object_id=share.id, 
                company_id=c.id, 
                save=True)

        url, parsed = self.prepare_urls(
            'v1:share-search-by-hashtags', subdomain=self.company.subdomain)

        response = self.client.post(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('count'))
        self.assertEqual(content['count'], 100)
        self.assertTrue(content.has_key('next'))
        self.assertTrue(content.has_key('previous'))
        self.assertTrue(content.has_key('results'))

        
    def test_get_shares_by_user(self):
        """
        Ensure we can get list of shares by user
        """
        url, parsed = self.prepare_urls('v1:share-get-by-user', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        # self.assertTrue(content.has_key('count'))
        # self.assertTrue(content.has_key('next'))
        # self.assertTrue(content.has_key('previous'))
        # self.assertTrue(content.has_key('results'))

    def test_create_multiple(self):
        """
        Ensure we can create multiple
        """
        contact = Contact.objects.first()

        valid_data = [{'share_to':self.user.id, 'note':'test message', 'contact_id': contact.id}]
        url, parsed = self.prepare_urls('v1:share-create-multiple', subdomain=self.company.subdomain)
        
        response = self.client.post(url, valid_data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, valid_data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertTrue(content.has_key('notification'))

    def test_share_filter(self):
        company = self.company
        user = self.user

        for i in range(0,100):
            c = ContactFactory(owner=self.user, company_id=self.company.id)
            share = ShareFactory(
                contact=c,
                share_to=user,
                share_from=user,
                owner=user,
                company_id=company.id,
                note='test'
                )
        for i in range(0,100):
            c = ContactFactory(owner=self.user, company_id=self.company.id)
            share = ShareFactory(
                contact=c,
                share_to=user,
                share_from=user,
                owner=user,
                company_id=company.id,
                note='tset'
                )

        params = {'search':'test'}
        url, parsed = self.prepare_urls('v1:share-list', subdomain=self.company.subdomain)
        response = self.client.get(url, params, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, params, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content['count'], 100)