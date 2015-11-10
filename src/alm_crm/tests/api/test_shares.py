import simplejson as json

from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.models import (
    Share,
    HashTag,
    HashTagReference,
    )
from . import APITestMixin

class ShareAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

	def test_search_by_hashtags(self):
        company = self.company
        user = self.user

        for i in range(0,100):
        	c = Contact(
	            vcard__fn='test', 
	            owner=user, 
	            company_id=company.id)
        	c.save()
            share = Share(
                contact=c,
                share_to=user,
                share_from=user,
           		owner=user,
           		company_id=company.id
                )
            share.save()
            hash_tag = HashTag(text='#test')
            hash_tag.save()
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Share, 
                object_id=share.id, 
                company_id=c.id, 
                save=True)

        url, parsed = self.prepare_urls(
            'v1:share-search_by_hashtags', subdomain=self.company.subdomain)

        response = self.client.get(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        assertEqual(response.count, 100)

        
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
        self.assertTrue(content.has_key('count'))
        self.assertTrue(content.has_key('next'))
        self.assertTrue(content.has_key('previous'))
        self.assertTrue(content.has_key('results'))
