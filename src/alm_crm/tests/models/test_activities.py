import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import (
    ContactFactory, 
    SalesCycleFactory, 
    ActivityFactory,
    HashTagFactory,
    HashTagReferenceFactory,
    )
from alm_crm.models import (
    Activity, 
    SalesCycle,
    HashTag,
    HashTagReference,
    )
from alm_crm.filters import ActivityFilter
from . import TestMixin


class ActivityTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_get_activities_panel(self):
        """
        Ensure we can get proper information for dashboard panels
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(contact=contact, company_id=self.company.id)
        total_count = 10
        my_count = 5

        my = []
        total = []

        for i in range(total_count-my_count):
            a = ActivityFactory(sales_cycle=sales_cycle, owner=account2.user, company_id=self.company.id, deadline=timezone.now()+relativedelta.relativedelta(months=1))
            total.append(a)

        for i in range(my_count):
            a = ActivityFactory(sales_cycle=sales_cycle, owner=self.user, company_id=self.company.id, deadline=timezone.now()+relativedelta.relativedelta(months=1))
            my.append(a)
            total.append(a)

        a = my[0]
        a.deadline = timezone.now()-relativedelta.relativedelta(months=1)
        a.save()

        a = my[1]
        a.deadline = timezone.now()
        a.save()

        a = my[2]
        a.date_finished = timezone.now()
        a.save()

        a = my[3]
        a.date_finished = timezone.now()
        a.save()

        a = total[0]
        a.deadline = timezone.now()-relativedelta.relativedelta(months=1)
        a.save()

        a = total[1]
        a.deadline = timezone.now()
        a.save()

        a = total[2]
        a.date_finished = timezone.now()
        a.save()

        panel_info = Activity.get_panel_info(
            company_id=self.company.id, user_id=self.user.id)

        self.assertEqual(panel_info['all']['total'], 10)
        self.assertEqual(panel_info['my']['total'], 5)

        self.assertEqual(panel_info['all']['completed'], 3)
        self.assertEqual(panel_info['my']['completed'], 2)

        self.assertEqual(panel_info['all']['overdue'], 2)
        self.assertEqual(panel_info['my']['overdue'], 1)

        self.assertEqual(panel_info['all']['by_period']['days'], 10)
        self.assertEqual(panel_info['my']['by_period']['days'], 5)


    def test_change_sales_cycle_status_on_create_delete(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        self.assertEqual(sales_cycle.status, SalesCycle.NEW)

        a = ActivityFactory(
            sales_cycle=sales_cycle, 
            owner=self.user, 
            company_id=self.company.id
            )
        self.assertEqual(sales_cycle.status, SalesCycle.PENDING)

        a.delete()
        self.assertEqual(sales_cycle.status, SalesCycle.NEW)

    def test_change_sales_cycle_status_on_move(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, 
            company_id=self.company.id
            )

        self.assertEqual(sales_cycle.status, SalesCycle.NEW)

        a = ActivityFactory(
            sales_cycle=sales_cycle, 
            owner=self.user, 
            company_id=self.company.id
            )
        self.assertEqual(sales_cycle.status, SalesCycle.PENDING)

        sales_cycle2 = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        a.move(sales_cycle2.id)
        sales_cycle2 = SalesCycle.objects.get(id=sales_cycle2.id)

        self.assertEqual(sales_cycle.status, SalesCycle.NEW)
        self.assertEqual(sales_cycle2.status, SalesCycle.PENDING)

    def test_company_feed(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        for i in range(5):
            a = ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id
                )
            a.spray(self.company.id, self.account)

        for i in range(3):
            a = ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=account2.user, 
                company_id=self.company.id
                )
            a.spray(self.company.id, account2)
        
        company_feed = Activity.company_feed(
            company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(company_feed['feed'].count(), 8)
        self.assertEqual(company_feed['not_read'], 3)

    def test_user_activities(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        for i in range(5):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id
                )

        for i in range(3):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=account2.user, 
                company_id=self.company.id)
        
        feed = Activity.user_activities(
            company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(feed.count(), 5)

        feed = Activity.user_activities(
            company_id=self.company.id, user_id=account2.user.id)
        self.assertEqual(feed.count(), 3)

    def test_my_tasks(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        for i in range(5):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now()
                )
        for i in range(2):
            ActivityFactory(sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now(), 
                assignee=account2.user
                )
        for i in range(3):
            ActivityFactory(sales_cycle=sales_cycle, 
                owner=account2.user, company_id=self.company.id)
        feed = Activity.my_tasks(company_id=self.company.id, 
            user_id=self.user.id)
        self.assertEqual(feed.count(), 5)

        feed = Activity.my_tasks(
            company_id=self.company.id, user_id=account2.user.id)
        self.assertEqual(feed.count(), 2)

    def test_my_feed(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        contact2 = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        sales_cycle2 = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        sales_cycle3 = SalesCycleFactory(
            contact=contact2, company_id=self.company.id)

        for i in range(5):
            a = ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id
                )
            a.spray(self.company.id, self.account)

        for i in range(2):
            a = ActivityFactory(
                sales_cycle=sales_cycle2, 
                owner=self.user, 
                company_id=self.company.id)
            a.spray(self.company.id, self.account)

        for i in range(3):
            a = ActivityFactory(
                sales_cycle=sales_cycle3, 
                owner=self.user, 
                company_id=self.company.id)
            a.spray(self.company.id, self.account)

        for i in range(4):
            a = ActivityFactory(
                sales_cycle=sales_cycle3, 
                owner=account2.user, 
                company_id=self.company.id)
            a.spray(self.company.id, account2)
        
        my_feed = Activity.my_feed(
            company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(my_feed['feed'].count(), 14)
        self.assertEqual(my_feed['not_read'], 4)

        self.account.unfollow_list.add(contact)
        my_feed = Activity.my_feed(
            company_id=self.company.id, 
            user_id=self.user.id)
        self.assertEqual(my_feed['feed'].count(), 7)
        self.assertEqual(my_feed['not_read'], 4)

    def test_mark_as_read(self):
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        not_read_acts = []
        for i in range(5):
            a = ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id
                )
            a.spray(self.company.id, self.account)

        for i in range(4):
            a = ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=account2.user, 
                company_id=self.company.id
                )
            a.spray(self.company.id, account2)
            not_read_acts.append(a.id)
        
        my_feed = Activity.my_feed(
            company_id=self.company.id, 
            user_id=self.user.id)
        self.assertEqual(my_feed['feed'].count(), 9)
        self.assertEqual(my_feed['not_read'], 4)

        read = Activity.mark_as_read(
            company_id=self.company.id, 
            user_id=self.user.id, 
            act_ids=not_read_acts)
        self.assertEqual(read, 4)

        my_feed = Activity.my_feed(
            company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(my_feed['feed'].count(), 9)
        self.assertEqual(my_feed['not_read'], 0)

    def test_get_calendar(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        for i in range(1):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now()+relativedelta.relativedelta(months=1)
                )
        for i in range(2):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now(), 
                need_preparation=True
                )
        for i in range(3):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now(), 
                need_preparation=True, 
                date_finished=timezone.now()
                )
        for i in range(4):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now(), 
                need_preparation=False)
        for i in range(5):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id
                )

        activities = Activity.get_calendar(
            company_id=self.company.id, 
            user_id=self.user.id, 
            dt=timezone.now()
            )
        self.assertEqual(len(activities), 14)

    def test_search_by_hashtags(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        for i in range(0,100):
            ActivityFactory(
                sales_cycle=sales_cycle, 
                owner=self.user, 
                company_id=self.company.id, 
                deadline=timezone.now()+relativedelta.relativedelta(months=1)
                )
        activities = Activity.objects.filter(company_id=self.company.id)
        for activity in activities:
            hash_tag = HashTagFactory(
                text='#test')
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Activity, 
                object_id=activity.id, 
                company_id=self.company.id, 
                save=True)
        activities = Activity.search_by_hashtags(
            company_id=self.company.id, search_query='#test')
        self.assertEqual(activities.count(), 100)

        for activity in activities[0:30]:
            hash_tag = HashTagFactory(
                text='#test2')
            HashTagReference.build_new(
                hash_tag.id, 
                content_class=Activity, 
                object_id=activity.id, 
                company_id=self.company.id, 
                save=True)
        activities = Activity.search_by_hashtags(
            company_id=self.company.id, search_query='#test, #test2')
        self.assertEqual(activities.count(), 30)


    def test_create_activity(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        SalesCycle.create_globalcycle(
            **{'company_id': self.company.id,
               'owner_id': self.user.id,
               'contact_id': contact.id
            }
        )

        valid_data = {'sales_cycle_id':sales_cycle.id, 'description':'test message', 'contact_id': contact.id}

        activity = Activity.create_activity(
            company_id=self.company.id, 
            user_id=self.user.id, 
            data=valid_data
            )
        self.assertEqual(activity.description, 'test message')
        self.assertEqual(activity.sales_cycle.id, sales_cycle.id)
        self.assertEqual(activity.hashtags.count(), 0)

        valid_data_with_hashtag = {
            'sales_cycle_id':sales_cycle.id, 
            'description':'test message #tag',
             'contact_id': contact.id
            }

        activity = Activity.create_activity(
            company_id=self.company.id, 
            user_id=self.user.id, 
            data=valid_data_with_hashtag
            )
        self.assertEqual(activity.description, 'test message #tag')
        self.assertEqual(activity.sales_cycle.id, sales_cycle.id)
        self.assertEqual(activity.hashtags.count(), 1)

        valid_data_with_no_cycle = {
            'description':'test message2', 'contact_id': contact.id}

        activity = Activity.create_activity(
            company_id=self.company.id,
            user_id=self.user.id, 
            data=valid_data_with_no_cycle
            )
        self.assertEqual(activity.description, 'test message2')
        self.assertEqual(activity.sales_cycle.id, contact.global_sales_cycle.id)
        self.assertEqual(activity.hashtags.count(), 0)

    def test_move_activity(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle1 = SalesCycleFactory(
            contact=contact, company_id=self.company.id)
        sales_cycle2 = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        activity = ActivityFactory(
            sales_cycle=sales_cycle1, 
            owner=self.user, 
            company_id=self.company.id
        )

        self.assertEqual(activity.sales_cycle.id, sales_cycle1.id)

        activity.move(sales_cycle2.id)
        self.assertEqual(activity.sales_cycle.id, sales_cycle2.id)

    def test_finish_activity(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle1 = SalesCycleFactory(
            contact=contact, company_id=self.company.id)

        activity = ActivityFactory(
            sales_cycle=sales_cycle1, 
            owner=self.user, 
            company_id=self.company.id,
            deadline=timezone.now(),
        )

        self.assertEqual(activity.result, None)
        self.assertEqual(activity.date_finished, None)

        activity.finish("It's finished")
        self.assertEqual(activity.result, "It's finished")
        self.assertNotEqual(activity.date_finished, None)

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
        self.assertEqual(30, Activity.objects.all().count())
        queryset = ActivityFilter({'search':'test'}, Activity.objects.all()).qs
        self.assertEqual(20, queryset.count())
