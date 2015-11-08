import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.factories import ContactFactory, SalesCycleFactory
from alm_crm.models import SalesCycle

from . import APITestMixin

class SalesCycleAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.sales_cycles_count = 5
        self.setUpSalesCycles(self.sales_cycles_count)

    def setUpSalesCycles(self, sales_cycles_count):
        contact = ContactFactory(company_id=self.company.id)
        for i in range(sales_cycles_count):
            SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)

    def test_get_sales_cycles(self):
        """
        Ensure we can get list of sales_cycles
        """
        url, parsed = self.prepare_urls('v1:sales_cycle-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertEqual(content['count'], self.sales_cycles_count)

    def test_get_sales_cycles_with_ids(self):
        """
        Ensure we can get list of sales_cycles with specific ids
        """
        sales_cycles_ids = map(lambda x: x.id, SalesCycle.objects.all()[:3])
        url, parsed = self.prepare_urls('v1:sales_cycle-list', query={'ids': ','.join(str(x) for x in sales_cycles_ids)}, subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertEqual(content['count'], 3)

        url, parsed = self.prepare_urls('v1:sales_cycle-list', query={'ids': ''}, subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertEqual(content['count'], 0)

    def get_statistics(self):
        """
        Ensure we can get statistics for sales_cycles
        """
        url, parsed = self.prepare_urls('v1:sales_cycle-statistics', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertTrue(content.has_key('all_sales_cycles'))
        self.assertTrue(content.has_key('new_sales_cycles'))
        self.assertTrue(content.has_key('successful_sales_cycles'))
        self.assertTrue(content.has_key('failed_sales_cycles'))
        self.assertTrue(content.has_key('open_sales_cycles'))
        self.assertTrue(content.has_key('my_sales_cycles'))
        self.assertTrue(content.has_key('my_new_sales_cycles'))
        self.assertTrue(content.has_key('my_successful_sales_cycles'))
        self.assertTrue(content.has_key('my_failed_sales_cycles'))
        self.assertTrue(content.has_key('my_open_sales_cycles'))

    def test_get_all_sales_cycles(self):
        """
        Ensure we can get list of all sales_cycles
        """
        url, parsed = self.prepare_urls('v1:sales_cycle-all', subdomain=self.company.subdomain)
        
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
        self.assertEqual(content['count'], self.sales_cycles_count)

    def test_get_all_new_sales_cycles(self):
        """
        Ensure we can get list of all new sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-new/all', subdomain=self.company.subdomain)
        
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

    def test_get_all_pending_sales_cycles(self):
        """
        Ensure we can get list of all pending sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-pending/all', subdomain=self.company.subdomain)
        
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

    def test_get_all_successful_sales_cycles(self):
        """
        Ensure we can get list of all successful sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-successful/all', subdomain=self.company.subdomain)
        
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

    def test_get_all_failed_sales_cycles(self):
        """
        Ensure we can get list of all failed sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-failed/all', subdomain=self.company.subdomain)
        
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

    def test_get_my_sales_cycles(self):
        """
        Ensure we can get list of my sales_cycles
        """
        url, parsed = self.prepare_urls('v1:sales_cycle-my', subdomain=self.company.subdomain)
        
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
        self.assertEqual(content['count'], self.sales_cycles_count)

    def test_get_my_new_sales_cycles(self):
        """
        Ensure we can get list of my new sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-new/my', subdomain=self.company.subdomain)
        
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

    def test_get_my_pending_sales_cycles(self):
        """
        Ensure we can get list of my pending sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-pending/my', subdomain=self.company.subdomain)
        
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

    def test_get_my_successful_sales_cycles(self):
        """
        Ensure we can get list of my successful sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-successful/my', subdomain=self.company.subdomain)
        
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

    def test_get_my_failed_sales_cycles(self):
        """
        Ensure we can get list of my failed sales_cycles
        """

        url, parsed = self.prepare_urls('v1:sales_cycle-failed/my', subdomain=self.company.subdomain)
        
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
