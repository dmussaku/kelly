import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.models import Filter
from alm_crm.factories import FilterFactory
from alm_crm.serializers import FilterSerializer

from . import APITestMixin

class FilterAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.filters_count = 5
        self.setUpFilters(self.filters_count)

    def setUpFilters(self, filters_count):
        for i in range(filters_count):
            FilterFactory(owner_id=self.user.id, company_id=self.company.id)

    def test_get_filters(self):
        """
        Ensure we can get list of filters
        """
        url, parsed = self.prepare_urls('v1:filter-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(len(content), self.filters_count)

    def test_get_specific_filter(self):
        """
        Ensure we can get specific of filter by id
        """
        f = Filter.objects.first()
        url, parsed = self.prepare_urls('v1:filter-detail', subdomain=self.company.subdomain, kwargs={'pk':f.id})

        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_filter(self):
        """
        Ensure that we can create filter
        """
        data = {
            'title': 'Filter1',
            'filter_text': 'search_string',
        }

        url, parsed = self.prepare_urls('v1:filter-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertEqual(content['title'], 'Filter1')
        self.assertEqual(content['filter_text'], 'search_string')
        self.assertNotEqual(content['company_id'], None)
        self.assertNotEqual(content['owner'], None)

        url, parsed = self.prepare_urls('v1:filter-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.filters_count+1, len(content))
    
    def test_edit_filter(self):
        """
        Ensure that we can edit filter
        """
        f = Filter.objects.first()
        data = FilterSerializer(f).data

        data['title'] = 'Nestle'
        data['filter_text'] = 'search_string'

        url, parsed = self.prepare_urls('v1:filter-detail', subdomain=self.company.subdomain, kwargs={'pk':f.id})
        
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url, parsed = self.prepare_urls('v1:filter-detail', subdomain=self.company.subdomain, kwargs={'pk':f.id})
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(content['title'], 'Nestle')
        self.assertEqual(content['filter_text'], 'search_string')

    def test_delete_filter(self):
        """
        Ensure that we can delete filter
        """
        f = Filter.objects.first()

        url, parsed = self.prepare_urls('v1:filter-detail', subdomain=self.company.subdomain, kwargs={'pk':f.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url, parsed = self.prepare_urls('v1:filter-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.filters_count-1, len(content))

    def test_apply_filter(self):
        """
        Ensure that we can apply filter
        """
        f = Filter.objects.first()

        url, parsed = self.prepare_urls('v1:filter-apply', subdomain=self.company.subdomain, kwargs={'pk':f.id})
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        