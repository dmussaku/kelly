import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.models import Product
from alm_crm.factories import ProductFactory
from alm_crm.serializers import ProductSerializer

from . import APITestMixin

class ProductAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.products_count = 5
        self.setUpProducts(self.products_count)

    def setUpProducts(self, products_count):
        for i in range(products_count):
            ProductFactory(company_id=self.company.id)

    def test_get_products(self):
        """
        Ensure we can get list of products
        """
        url, parsed = self.prepare_urls('v1:product-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(len(content), self.products_count)

    def test_get_specific_product(self):
        """
        Ensure we can get specific of product by id
        """
        product = Product.objects.first()
        url, parsed = self.prepare_urls('v1:product-detail', subdomain=self.company.subdomain, kwargs={'pk':product.id})

        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self):
        """
        Ensure that we can create product
        """
        data = {
            'name': 'Product1',
            'description': '',
            'price': 0,
        }

        url, parsed = self.prepare_urls('v1:product-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertEqual(content['name'], 'Product1')
        self.assertEqual(content['description'], '')
        self.assertNotEqual(content['company_id'], None)
        self.assertNotEqual(content['owner'], None)

        url, parsed = self.prepare_urls('v1:product-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.products_count+1, len(content))
    
    def test_edit_product(self):
        """
        Ensure that we can edit product
        """
        product = Product.objects.first()
        data = ProductSerializer(product).data

        data['name'] = 'Nestle'
        data['description'] = 'Chocolate'

        url, parsed = self.prepare_urls('v1:product-detail', subdomain=self.company.subdomain, kwargs={'pk':product.id})
        
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url, parsed = self.prepare_urls('v1:product-detail', subdomain=self.company.subdomain, kwargs={'pk':product.id})
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(content['name'], 'Nestle')
        self.assertEqual(content['description'], 'Chocolate')

    def test_delete_product(self):
        """
        Ensure that we can delete product
        """
        product = Product.objects.first()
        data = ProductSerializer(product).data

        url, parsed = self.prepare_urls('v1:product-detail', subdomain=self.company.subdomain, kwargs={'pk':product.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url, parsed = self.prepare_urls('v1:product-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.products_count-1, len(content))
