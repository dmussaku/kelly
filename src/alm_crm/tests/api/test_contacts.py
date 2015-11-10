import simplejson as json

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.models import Contact
from alm_crm.factories import ContactFactory
from alm_crm.serializers import ContactSerializer

from . import APITestMixin

class ContactAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.contacts_count = 5
        self.setUpContacts(self.contacts_count)

    def setUpContacts(self, contacts_count):
        for i in range(contacts_count):
            ContactFactory(company_id=self.company.id)

    def test_get_contacts(self):
        """
        Ensure we can get list of contacts
        """
        url, parsed = self.prepare_urls('v1:contact-list', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(len(content), self.contacts_count)

    def test_get_specific_contact(self):
        """
        Ensure we can get specific of contact by id
        """
        contact = Contact.objects.first()
        url, parsed = self.prepare_urls('v1:contact-detail', subdomain=self.company.subdomain, kwargs={'pk':contact.id})

        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_cached_contacts(self):
        """
        Ensure we can get list of cached contacts
        """
        Contact.cache_all()

        url, parsed = self.prepare_urls('v1:contact-state', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(len(content), self.contacts_count)

    def test_create_contact_without_company(self):
        """
        Ensure that we can create contact
        """
        data = {
            "vcard": {
                "family_name":"Miss Eola",
                "given_name":"Kuhlman",
                "tels":[{"value":"1-982-854-2933x674","type":"HOME"},{"value":"(858)457-7988x7577","type":"HOME"}],
                "emails":[{"value":"winfred.beahan@gmail.com","type":"INTERNET"},{"value":"loberbrunner@schiller.biz","type":"INTERNET"},{"value":"zpurdy@keebler.net","type":"INTERNET"}],
                "adrs":[{"street_address":"668 Alba Mountains","region":"VonRuedenburgh","locality":"Maine","country_name":"Syrian Arab Republic","postal_code":"17421","type":"WORK"}],
                "categories":[{"data":"voluptatem"}],
                "notes":[],
                "titles":[{"data":"Psychologist, educational"}],
                "urls":[{"value":"http://feeney.com/","type":"github"}]
            },
            "tp":"user",
            "user_id":3,
        }

        url, parsed = self.prepare_urls('v1:contact-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('owner'))
        self.assertNotEqual(content['owner'], None)
        self.assertTrue(content.has_key('vcard'))
        self.assertNotEqual(content['vcard'], None)
        self.assertTrue(content.has_key('global_sales_cycle'))
        self.assertNotEqual(content['global_sales_cycle'], None)

        url, parsed = self.prepare_urls('v1:contact-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.contacts_count+1, len(content)) # added 1 contact

    def test_create_contact_with_company(self):
        """
        Ensure that we can create contact with company
        """
        data = {
            "vcard": {
                "family_name":"Miss Eola",
                "given_name":"Kuhlman",
                "tels":[{"value":"1-982-854-2933x674","type":"HOME"},{"value":"(858)457-7988x7577","type":"HOME"}],
                "emails":[{"value":"winfred.beahan@gmail.com","type":"INTERNET"},{"value":"loberbrunner@schiller.biz","type":"INTERNET"},{"value":"zpurdy@keebler.net","type":"INTERNET"}],
                "adrs":[{"street_address":"668 Alba Mountains","region":"VonRuedenburgh","locality":"Maine","country_name":"Syrian Arab Republic","postal_code":"17421","type":"WORK"}],
                "categories":[{"data":"voluptatem"}],
                "notes":[],
                "titles":[{"data":"Psychologist, educational"}],
                "urls":[{"value":"http://feeney.com/","type":"github"}]
            },
            "tp":"user",
            "user_id":3,
            "company_name":"Detroit Red Wings"
        }

        url, parsed = self.prepare_urls('v1:contact-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('owner'))
        self.assertNotEqual(content['owner'], None)
        self.assertTrue(content.has_key('vcard'))
        self.assertNotEqual(content['vcard'], None)
        self.assertTrue(content.has_key('global_sales_cycle'))
        self.assertNotEqual(content['global_sales_cycle'], None)
        self.assertTrue(content.has_key('parent'))
        self.assertNotEqual(content['parent'], None)
        self.assertTrue(content['parent'].has_key('global_sales_cycle'))
        self.assertNotEqual(content['parent']['global_sales_cycle'], None)

        url, parsed = self.prepare_urls('v1:contact-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.contacts_count+2, len(content)) # added 2 contacts: contact and its parent

    def test_edit_contact(self):
        """
        Ensure that we can edit contact
        """
        contact = Contact.objects.first()
        data = ContactSerializer(contact).data
        old_vcard_id = data['vcard']['id']

        data['vcard']['adrs'][0]['locality'] = 'Almaty'

        url, parsed = self.prepare_urls('v1:contact-detail', subdomain=self.company.subdomain, kwargs={'pk':contact.id})
        
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.put(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url, parsed = self.prepare_urls('v1:contact-detail', subdomain=self.company.subdomain, kwargs={'pk':contact.id})
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(content['vcard']['adrs'][0]['locality'], 'Almaty')
        self.assertNotEqual(content['vcard']['id'], old_vcard_id) # ensure that we really delete vcard and create new one

    def test_delete_contact(self):
        """
        Ensure that we can delete contact
        """
        contact = Contact.objects.first()
        data = ContactSerializer(contact).data
        old_vcard_id = data['vcard']['id']

        url, parsed = self.prepare_urls('v1:contact-detail', subdomain=self.company.subdomain, kwargs={'pk':contact.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url, parsed = self.prepare_urls('v1:contact-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.contacts_count-1, len(content))

    def test_get_statistics(self):
        """
        Ensure we can get statistics for contacts page
        """
        url, parsed = self.prepare_urls('v1:contact-statistics', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('shared'))
        self.assertTrue(content.has_key('all'))
        self.assertTrue(content.has_key('recentbase'))
        self.assertTrue(content.has_key('coldbase'))
        self.assertTrue(content.has_key('leadbase'))

    def test_get_contacts_with_ids(self):
        """
        Ensure we can get list of contacts with specific ids
        """
        contacts_ids = map(lambda x: x.id, Contact.objects.all()[:3])
        url, parsed = self.prepare_urls('v1:contact-list', query={'ids': ','.join(str(x) for x in contacts_ids)}, subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertEqual(len(content), 3)

        url, parsed = self.prepare_urls('v1:contact-list', query={'ids': ''}, subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = json.loads(response.content)
        self.assertEqual(len(content), 0)

    def test_get_all(self):
        """
        Ensure we can get all contacts
        """
        url, parsed = self.prepare_urls('v1:contact-all', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_recent(self):
        """
        Ensure we can get recent contacts
        """
        url, parsed = self.prepare_urls('v1:contact-recent', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_cold(self):
        """
        Ensure we can get cold contacts
        """
        url, parsed = self.prepare_urls('v1:contact-cold', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_lead(self):
        """
        Ensure we can get lead contacts
        """
        url, parsed = self.prepare_urls('v1:contact-lead', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
