import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.models import ContactList
from alm_crm.factories import ContactListFactory
from alm_crm.serializers import ContactListSerializer

from . import APITestMixin

class ContactListAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.contact_lists_count = 5
        self.setUpContactLists(self.contact_lists_count)

    def setUpContactLists(self, contact_lists_count):
        for i in range(contact_lists_count):
            ContactListFactory(owner_id=self.user.id, company_id=self.company.id)

    def test_get_contact_lists(self):
        """
        Ensure we can get list of contact_lists
        """
        url, parsed = self.prepare_urls('v1:contact_list-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(len(content), self.contact_lists_count)

    def test_get_specific_contact_list(self):
        """
        Ensure we can get specific of contact_list by id
        """
        contact_list = ContactList.objects.first()
        url, parsed = self.prepare_urls('v1:contact_list-detail', subdomain=self.company.subdomain, kwargs={'pk':contact_list.id})

        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_contact_list(self):
        """
        Ensure that we can create contact_list
        """
        data = {
            'title': 'ContactList1',
        }

        url, parsed = self.prepare_urls('v1:contact_list-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertEqual(content['title'], 'ContactList1')
        self.assertNotEqual(content['company_id'], None)
        self.assertNotEqual(content['owner'], None)

        url, parsed = self.prepare_urls('v1:contact_list-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.contact_lists_count+1, len(content))
    
    def test_edit_contact_list(self):
        """
        Ensure that we can edit contact_list
        """
        contact_list = ContactList.objects.first()
        data = ContactListSerializer(contact_list).data

        data['title'] = 'Nestle'

        url, parsed = self.prepare_urls('v1:contact_list-detail', subdomain=self.company.subdomain, kwargs={'pk':contact_list.id})
        
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url, parsed = self.prepare_urls('v1:contact_list-detail', subdomain=self.company.subdomain, kwargs={'pk':contact_list.id})
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(content['title'], 'Nestle')

    def test_delete_contact_list(self):
        """
        Ensure that we can delete contact_list
        """
        contact_list = ContactList.objects.first()
        data = ContactListSerializer(contact_list).data

        url, parsed = self.prepare_urls('v1:contact_list-detail', subdomain=self.company.subdomain, kwargs={'pk':contact_list.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url, parsed = self.prepare_urls('v1:contact_list-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.contact_lists_count-1, len(content))
