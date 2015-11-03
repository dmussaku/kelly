import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from . import APITestMixin

class AppStateAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

    def test_get_app_state(self):
        """
        Ensure we can get app_state
        """
        url, parsed = self.prepare_urls('v1:app_state-crm', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertNotEqual(content['hashtags'], None)
        self.assertNotEqual(content['categories'], None)
        self.assertNotEqual(content['constants'], None)

    def test_get_categories(self):
        """
        Ensure we can get raw categories
        """
        url, parsed = self.prepare_urls('v1:app_state-crm/categories', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertNotEqual(content['objects'], None)
        self.assertIsInstance(content['objects'], list)

    def test_get_hashtags(self):
        """
        Ensure we can get raw hashtags
        """
        url, parsed = self.prepare_urls('v1:app_state-crm/hashtags', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertNotEqual(content['objects'], None)
        self.assertIsInstance(content['objects'], list)

    # def test_search(self):
    #     """
    #     Ensure we can search by hashtags
    #     """
    #     url, parsed = self.prepare_urls('v1:app_state-crm/search', subdomain=self.company.subdomain)
        
    #     response = self.client.get(url, HTTP_HOST=parsed.netloc)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #     self.authenticate_user()
    #     response = self.client.get(url, HTTP_HOST=parsed.netloc)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     content = json.loads(response.content)
