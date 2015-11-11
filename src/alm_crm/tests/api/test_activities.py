import simplejson as json

from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.models import (
    Contact,
    Activity,
    SalesCycle,
    HashTag,
    HashTagReference,
)
from alm_crm.factories import ContactFactory, SalesCycleFactory, ActivityFactory

from . import APITestMixin

class ActivityAPITests(APITestMixin, APITestCase):
    def setUp(self):
        self.set_user()
        self.activities_count = 5
        self.setUpActivities(self.activities_count)

    def setUpActivities(self, activities_count):
        contact = ContactFactory(company_id=self.company.id, owner_id=self.user.id)
        sales_cycle = SalesCycleFactory(company_id=self.company.id, owner_id=self.user.id, contact=contact)
        for i in range(activities_count):
            ActivityFactory(company_id=self.company.id, owner_id=self.user.id, sales_cycle=sales_cycle)

    def test_get_statistics(self):
        """
        Ensure we can get statistics for activities page
        """
        url, parsed = self.prepare_urls('v1:activity-statistics', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('company_feed'))
        self.assertTrue(content.has_key('my_feed'))
        self.assertTrue(content.has_key('my_activities'))
        self.assertTrue(content.has_key('my_tasks'))

    def test_company_feed(self):
        """
        Ensure we can get company feed
        """
        url, parsed = self.prepare_urls('v1:activity-company-feed', subdomain=self.company.subdomain)
        
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

    def test_my_feed(self):
        """
        Ensure we can get my feed
        """
        url, parsed = self.prepare_urls('v1:activity-my-feed', subdomain=self.company.subdomain)
        
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

    def test_my_activities(self):
        """
        Ensure we can get my activities
        """
        url, parsed = self.prepare_urls('v1:activity-my-activities', subdomain=self.company.subdomain)
        
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

    def test_my_tasks(self):
        """
        Ensure we can get my tasks
        """
        url, parsed = self.prepare_urls('v1:activity-my-tasks', subdomain=self.company.subdomain)
        
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

    def test_mark_as_read(self):
        """
        Ensure we can mark as read
        """
        url, parsed = self.prepare_urls('v1:activity-read', subdomain=self.company.subdomain)
        
        response = self.client.post(url, [], HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, [], HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertTrue(content.has_key('count'))
        self.assertTrue(content.has_key('statistics'))

    def test_get_calendar(self):
        """
        Ensure we can get calendar
        """
        url, parsed = self.prepare_urls('v1:activity-calendar', subdomain=self.company.subdomain)
        
        response = self.client.post(url, {'dt': timezone.now()}, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, {'dt': timezone.now()}, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertTrue(content.has_key('calendar_data'))

    def test_search_by_hashtags(self):
        company = self.company
        user = self.user
        c = Contact(
            vcard__fn='test', 
            owner=user, 
            company_id=company.id)
        c.save()
        sales_cycle = c.sales_cycles.first()
        for i in range(0,100):
            activity = Activity(
                title='test'+str(i),
                owner=user,
                company_id=company.id,
                sales_cycle=sales_cycle,
                )
            activity.save()
            hash_tag = HashTag(text='#test')
            hash_tag.save()
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Activity, 
                object_id=activity.id, 
                company_id=c.id, 
                save=True)

        url, parsed = self.prepare_urls(
            'v1:activity-search_by_hashtags', subdomain=self.company.subdomain)

        response = self.client.get(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        assertEqual(response.count, 100)

    def test_create_multiple(self):
        """
        Ensure we can create multiple
        """
        contact = Contact.objects.first()
        sales_cycle = contact.sales_cycles.first()
        valid_data = [{'sales_cycle_id':sales_cycle.id, 'description':'test message', 'contact_id': contact.id}]
        url, parsed = self.prepare_urls('v1:activity-create-multiple', subdomain=self.company.subdomain)
        
        response = self.client.post(url, valid_data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, valid_data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertTrue(content.has_key('notification'))
        