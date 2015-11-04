import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.renderers import JSONRenderer

from alm_crm.models import ProductGroup
from alm_crm.factories import ProductGroupFactory, ProductFactory
from alm_crm.serializers import ProductGroupSerializer

from . import APITestMixin

class ProductGroupAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.product_groups_count = 1
        self.setUpProductGroups(self.product_groups_count)

    def setUpProductGroups(self, product_groups_count):
        self.products = [ProductFactory(company_id=self.company.id) for i in range(5)]

        for i in range(product_groups_count):
            ProductGroupFactory(company_id=self.company.id, products=self.products)

    def test_get_product_groups(self):
        """
        Ensure we can get list of product_groups
        """
        url, parsed = self.prepare_urls('v1:product_group-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(len(content), self.product_groups_count)

    def test_get_specific_product_group(self):
        """
        Ensure we can get specific of product_group by id
        """
        product_group = ProductGroup.objects.first()
        url, parsed = self.prepare_urls('v1:product_group-detail', subdomain=self.company.subdomain, kwargs={'pk':product_group.id})

        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_group(self):
        """
        Ensure that we can create product_group
        """
        data = {
            'title': 'ProductGroup1',
            'products': [p.id for p in self.products],
        }

        url, parsed = self.prepare_urls('v1:product_group-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertEqual(content['title'], 'ProductGroup1')

        url, parsed = self.prepare_urls('v1:product_group-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.product_groups_count+1, len(content))
    
    def test_edit_product_group(self):
        """
        Ensure that we can edit product_group
        """
        product_group = ProductGroup.objects.first()
        data = ProductGroupSerializer(product_group).data

        data['title'] = 'ProductGroup2'

        url, parsed = self.prepare_urls('v1:product_group-detail', subdomain=self.company.subdomain, kwargs={'pk':product_group.id})
        
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url, parsed = self.prepare_urls('v1:product_group-detail', subdomain=self.company.subdomain, kwargs={'pk':product_group.id})
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(content['title'], 'ProductGroup2')

    def test_delete_product_group(self):
        """
        Ensure that we can delete product_group
        """
        product_group = ProductGroup.objects.first()
        data = ProductGroupSerializer(product_group).data

        url, parsed = self.prepare_urls('v1:product_group-detail', subdomain=self.company.subdomain, kwargs={'pk':product_group.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url, parsed = self.prepare_urls('v1:product_group-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.product_groups_count-1, len(content))
