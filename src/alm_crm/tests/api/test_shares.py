import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from . import APITestMixin

class ShareAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

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
