import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from . import APITestMixin

class MilestoneAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

    def test_get_milestones(self):
        """
        Ensure we can get list of milestones
        """
        url, parsed = self.prepare_urls('v1:milestone-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertGreaterEqual(len(content), 2)
