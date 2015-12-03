import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from . import APITestMixin

class AppStateAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()

    def test_funnel(self):
        """
        Ensure we can get funnel
        """
        url, parsed = self.prepare_urls('v1:report-funnel', subdomain=self.company.subdomain)
        
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('funnel'))
        self.assertTrue(content.has_key('total'))
        self.assertTrue(content.has_key('undefined'))
        self.assertTrue(content.has_key('report_name'))
        self.assertEqual(content['report_name'], 'funnel')

    def test_realtime_funnel(self):
        """
        Ensure we can get realtime funnel
        """
        url, parsed = self.prepare_urls('v1:report-realtime-funnel', subdomain=self.company.subdomain)
        
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('funnel'))
        self.assertTrue(content.has_key('total'))
        self.assertTrue(content.has_key('undefined'))
        self.assertTrue(content.has_key('report_name'))
        self.assertEqual(content['report_name'], 'realtime_funnel')

    def test_product_report(self):
        """
        Ensure we can get product report
        """
        url, parsed = self.prepare_urls('v1:report-product-report', subdomain=self.company.subdomain)
        
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('products'))
        self.assertTrue(content.has_key('report_name'))
        self.assertEqual(content['report_name'], 'product_report')

    def test_activity_feed(self):
        """
        Ensure we can get activity feed
        """
        url, parsed = self.prepare_urls('v1:report-activity-feed', subdomain=self.company.subdomain)
        
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, {}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('report_data'))
        self.assertTrue(content.has_key('report_name'))
        self.assertEqual(content['report_name'], 'activity_feed')
