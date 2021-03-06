import simplejson as json
import dateutil.relativedelta as relativedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from alm_crm.factories import (
    ContactFactory, 
    ActivityFactory, 
    SalesCycleFactory
    )
from alm_crm.models import (
    Contact,
    Activity,
    SalesCycle,
    Contact,
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
        url, parsed = self.prepare_urls(
            'v1:activity-statistics', subdomain=self.company.subdomain)
        
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('company_feed'))
        self.assertTrue(content.has_key('my_feed'))
        self.assertTrue(content.has_key('user_activities'))
        self.assertTrue(content.has_key('my_tasks'))

    def test_company_feed(self):
        """
        Ensure we can get company feed
        """
        url, parsed = self.prepare_urls(
            'v1:activity-company-feed', subdomain=self.company.subdomain)
        
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
        url, parsed = self.prepare_urls(
            'v1:activity-my-feed', subdomain=self.company.subdomain)
        
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

    def test_user_activities(self):
        """
        Ensure we can get user activities
        """
        url, parsed = self.prepare_urls(
            'v1:activity-user-activities', subdomain=self.company.subdomain)
        
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
        url, parsed = self.prepare_urls(
            'v1:activity-my-tasks', subdomain=self.company.subdomain)
        
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
        url, parsed = self.prepare_urls(
            'v1:activity-read', subdomain=self.company.subdomain)
        
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
        url, parsed = self.prepare_urls(
            'v1:activity-calendar', subdomain=self.company.subdomain)
        
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
        c = ContactFactory(owner=self.user, company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            owner=self.user, 
            company_id=self.company.id,
            contact=c)
        for i in range(0,100):
            a = ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user,
                company_id=self.company.id)
            hash_tag = HashTag(text='#test')
            hash_tag.save()
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Activity, 
                object_id=a.id, 
                company_id=c.id, 
                save=True)

        url, parsed = self.prepare_urls(
            'v1:activity-search-by-hashtags', subdomain=self.company.subdomain)

        response = self.client.post(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(
            url, {'q': '#test'}, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('count'))
        self.assertEqual(content['count'], 100)
        self.assertTrue(content.has_key('next'))
        self.assertTrue(content.has_key('previous'))
        self.assertTrue(content.has_key('results'))

    def test_create_activity(self):
        """
        Ensure that we can create activity
        """
        contact = Contact.objects.first()
        sales_cycle = contact.sales_cycles.first()

        data = {
            "owner": self.user.id,
            "sales_cycle_id": sales_cycle.id,
            "description": "test text",
        }

        url, parsed = self.prepare_urls('v1:activity-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('owner'))
        self.assertNotEqual(content['owner'], None)
        self.assertTrue(content.has_key('company_id'))
        self.assertNotEqual(content['company_id'], None)

        url, parsed = self.prepare_urls('v1:activity-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.activities_count+1, content['count']) # added 1 activity

    def test_create_planned_activity(self):
        """
        Ensure that we can create planned activity
        """
        contact = Contact.objects.first()
        sales_cycle = contact.sales_cycles.first()

        data = {
            "owner": self.user.id,
            "sales_cycle_id": sales_cycle.id,
            "description": "test text",
            "deadline": timezone.now(),
        }

        url, parsed = self.prepare_urls('v1:activity-list', subdomain=self.company.subdomain)
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertTrue(content.has_key('owner'))
        self.assertNotEqual(content['owner'], None)
        self.assertTrue(content.has_key('company_id'))
        self.assertNotEqual(content['company_id'], None)

        url, parsed = self.prepare_urls('v1:activity-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.activities_count+1, content['count']) # added 1 activity

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

    def test_delete(self):
        """
        Ensure we can delete activity
        """
        activity = Activity.objects.first()
        url, parsed = self.prepare_urls('v1:activity-detail', subdomain=self.company.subdomain, kwargs={'pk': activity.id})
        
        response = self.client.delete(url, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.delete(url, HTTP_HOST=parsed.netloc, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url, parsed = self.prepare_urls('v1:activity-list', subdomain=self.company.subdomain)
        response = self.client.get(url, HTTP_HOST=parsed.netloc)
        content = json.loads(response.content)
        self.assertEqual(self.activities_count-1, content['count']) # deleted 1 activity

    def test_move_activity(self):
        """
        Ensure we can move activity to another sales cycle
        """
        activity = Activity.objects.first()
        sc = SalesCycle.objects.first()

        data = {
            'sales_cycle_id': sc.id
        }

        url, parsed = self.prepare_urls('v1:activity-move', subdomain=self.company.subdomain, kwargs={'pk': activity.id})
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertTrue(content.has_key('prev_sales_cycle'))
        self.assertTrue(content.has_key('new_sales_cycle'))
        self.assertTrue(content.has_key('activity'))

    def test_finish_activity(self):
        """
        Ensure we can finish activity
        """
        activity = Activity.objects.first()

        data = {
            'result': 'result text'
        }

        url, parsed = self.prepare_urls('v1:activity-finish', subdomain=self.company.subdomain, kwargs={'pk': activity.id})
        
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.post(url, data, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_activity_filter(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        for i in range(0,10):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user,
                title='test', 
                company_id=self.company.id, 
                deadline=timezone.now()+relativedelta.relativedelta(months=1)
                )
        for i in range(0,10):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user,
                title='tset',
                description='test', 
                company_id=self.company.id, 
                deadline=timezone.now()+relativedelta.relativedelta(months=1)
                )
        for i in range(0,10):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user,
                title='tset', 
                company_id=self.company.id, 
                deadline=timezone.now()+relativedelta.relativedelta(months=1)
                )

        params = {'search':'test'}
        url, parsed = self.prepare_urls('v1:activity-list', subdomain=self.company.subdomain)
        response = self.client.get(url, params, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_user()
        response = self.client.get(url, params, HTTP_HOST=parsed.netloc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content['count'], 20)