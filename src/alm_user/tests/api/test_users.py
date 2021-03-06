import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.tests.api import APITestMixin

class UserApiTestCase(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

    def test_change_password(self):
    	url, parsed = self.prepare_urls(
    		'v1:user-change-password', subdomain=self.company.subdomain)
        new_password = '1234'
        data = {
        	"old_password":"123",
        	"new_password":new_password,
        	"new_password_check":new_password
        	}
        response = self.client.post(url, data, format='json', HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, format='json', HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content['success'], True)

    def test_follow_unfollow(self):
        url, parsed = self.prepare_urls(
            'v1:user-follow-unfollow', subdomain=self.company.subdomain)

        response = self.client.post(url, [], format='json', HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, [], format='json', HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
