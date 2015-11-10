import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase
from alm_crm.serializers import MilestoneSerializer
from alm_crm.models import Milestone

from . import APITestMixin

class MilestoneAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

    def test_get_milestones(self):
        """
        Ensure we can get list of milestones
        """
        url, parsed = self.prepare_urls(
            'v1:milestone-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertGreaterEqual(len(content), 2)

    def test_post_milestones(self):
        url, parsed = self.prepare_urls(
            'v1:milestone-bulk-edit', subdomain=self.company.subdomain)
        milestones = Milestone.objects.filter(company_id=self.company.id)
        test_data = [MilestoneSerializer(obj).data for obj in milestones]
        test_data.append({"title":"tes tes","color_code":"#F4B59C","is_system":0,"sort":7})
        test_data.append({"title":"test2 test 2","color_code":"#9CE5F4","is_system":0,"sort":8})
        package = {'milestones': test_data, 'sales_cycles':[]}
        response = self.client.post(url, package, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, package, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(len(content.get('milestones',"")), len(test_data))


