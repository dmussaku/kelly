import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.factories import ContactFactory, SalesCycleFactory, ProductFactory
from alm_crm.models import Contact, SalesCycle, Milestone

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
        self.assertEqual(len(content), 3)

        url, parsed = self.prepare_urls('v1:sales_cycle-list', query={'ids': ''}, subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertEqual(len(content), 0)

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

    def test_get_activities(self):
        """
        Ensure we can get list of activities for sales_cycle
        """
        sc = SalesCycle.objects.first()

        url, parsed = self.prepare_urls('v1:sales_cycle-activities', subdomain=self.company.subdomain, kwargs={'pk': sc.id})
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_milestone(self):
        """
        Ensure we can change sales cycle's milestone
        """
        sc = SalesCycle.objects.first()

        data = {
            'milestone_id': Milestone.objects.first().id
        }

        url, parsed = self.prepare_urls('v1:sales_cycle-change-milestone', subdomain=self.company.subdomain, kwargs={'pk': sc.id})
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """
        Ensure we can delete sales cycle
        """
        sales_cycle = SalesCycle.objects.first()
        url, parsed = self.prepare_urls('v1:sales_cycle-detail', subdomain=self.company.subdomain, kwargs={'pk': sales_cycle.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url, parsed = self.prepare_urls('v1:sales_cycle-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.sales_cycles_count-1, content['count']) # deleted 1 sales_cycle

        contact = ContactFactory(company_id=self.company.id)
        global_sales_cycle = SalesCycle.create_globalcycle(
                                **{'company_id': self.company.id,
                                   'owner_id': self.user.id,
                                   'contact_id': contact.id
                                }
                            )
        url, parsed = self.prepare_urls('v1:sales_cycle-detail', subdomain=self.company.subdomain, kwargs={'pk': global_sales_cycle.id})

        response = self.client.delete(url, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url, parsed = self.prepare_urls('v1:sales_cycle-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.sales_cycles_count, content['count']) # nothing was deleted

    def test_change_products(self):
        """
        Ensure we can change sales cycle's products
        """
        sc = SalesCycle.objects.first()
        p = ProductFactory(owner=self.user, company_id=self.company.id)

        data = {
            'product_ids': [p.id]
        }

        url, parsed = self.prepare_urls('v1:sales_cycle-change-products', subdomain=self.company.subdomain, kwargs={'pk': sc.id})
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_succeed(self):
        """
        Ensure we can close sales_cycle successfully
        """
        sc = SalesCycle.objects.first()
        p = ProductFactory(owner=self.user, company_id=self.company.id)
        sc = sc.change_products(product_ids=[p.id], user_id=self.user.id, company_id=self.company.id)

        data = {
            'stats': {
                p.id: 10
            }
        }

        url, parsed = self.prepare_urls('v1:sales_cycle-succeed', subdomain=self.company.subdomain, kwargs={'pk': sc.id})
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail(self):
        """
        Ensure we can close sales_cycle with failure
        """
        sc = SalesCycle.objects.first()
        p = ProductFactory(owner=self.user, company_id=self.company.id)
        sc = sc.change_products(product_ids=[p.id], user_id=self.user.id, company_id=self.company.id)

        data = {
            'stats': {
                p.id: 10
            }
        }

        url, parsed = self.prepare_urls('v1:sales_cycle-fail', subdomain=self.company.subdomain, kwargs={'pk': sc.id})
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_cycle_filter(self):
        contact = ContactFactory(company_id=self.company.id)
        for i in range(0,10):
            SalesCycleFactory(
                contact=contact, 
                owner=self.user,
                title='test', 
                company_id=self.company.id,
                )
        for i in range(0,10):
            SalesCycleFactory(
                contact=contact, 
                owner=self.user,
                title='tset',
                description='test', 
                company_id=self.company.id,
                )
        for i in range(0,10):
            SalesCycleFactory(
                contact=contact, 
                owner=self.user,
                title='tset', 
                company_id=self.company.id,
                )

        params = {'search':'test'}
        url, parsed = self.prepare_urls('v1:sales_cycle-list', subdomain=self.company.subdomain)
        response = self.client.get(url, params, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, params, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content['count'], 20)