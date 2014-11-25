import os
from django.test import TestCase
from django.utils.unittest import skipIf
from django.utils import timezone
from tastypie.test import ResourceTestCase
from alm_crm.models import (
    Contact,
    CRMUser,
    Activity,
    SalesCycle,
    Product,
    Mention,
    Feedback,
    Value,
    Comment,
    )
from alm_vcard.models import VCard

class ContactTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'feedbacks.json']

    def setUp(self):
        super(ContactTestCase, self).setUp()
        self.contact1 = Contact.objects.get(pk=1)

    def test_assign_user(self):
        self.assertEqual(len(self.contact1.assignees.all()), 0)
        self.assertTrue(self.contact1.assign_user(user_id=1))
        self.assertEqual(len(self.contact1.assignees.all()), 1)

    def test_assign_user_to_contacts(self):
        for pk in range(1, 4):
            self.assertEqual(
                len(Contact.objects.get(pk=pk).assignees.all()), 0)
        self.assertTrue(
            Contact.assign_user_to_contacts(user_id=1, contact_ids=[1, 2]))
        self.assertTrue(
            Contact.assign_user_to_contacts(user_id=1, contact_ids=(3, 4)))
        for pk in range(1, 4):
            c = Contact.objects.get(pk=pk)
            self.assertEqual(len(c.assignees.all()), 1)

    def test_get_contacts_by_status(self):
        self.assertEqual(len(Contact.get_contacts_by_status(status=1)), 2)
        self.assertEqual(
            len(Contact.get_contacts_by_status(status=1, limit=1)), 1)

    def test_get_cold_base(self):
        self.assertEqual(len(Contact.get_cold_base()), 1)

    def test_change_status_without_save(self):
        self.assertEqual(self.contact1.status, 1)
        self.contact1.change_status(0)
        contact = Contact.objects.get(pk=self.contact1.pk)
        self.assertEqual(contact.status, 1)

    def test_change_status_with_save(self):
        self.assertEqual(self.contact1.status, 1)
        self.contact1.change_status(0, save=True)
        contact = Contact.objects.get(pk=self.contact1.pk)
        self.assertEqual(contact.status, 0)

    def test_upload_contacts(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/aliya.vcf')
        file_obj = open(file_path, "r").read()
        contact = Contact.upload_contacts(upload_type='vcard',
                                          file_obj=file_obj)
        self.assertEqual(contact.__class__, Contact)
        self.assertEqual(contact.vcard.__class__, VCard)
        addr = list(contact.vcard.adr_set.all())
        self.assertEqual(len(addr), 2)
        self.assertNotEqual(contact.name, "Unknown")

    def test_upload_contacts_by_vcard(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/aliya.vcf')
        file_obj = open(file_path, "r").read()
        contact = Contact._upload_contacts_by_vcard(file_obj)
        self.assertEqual(contact.__class__, Contact)
        self.assertEqual(contact.vcard.__class__, VCard)
        addr = list(contact.vcard.adr_set.all())
        self.assertEqual(len(addr), 2)
        self.assertNotEqual(contact.name, "Unknown")

    def test_filter_contacts_by_vcard(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/aliya.vcf')
        file_obj = open(file_path, "r").read()
        contacts = Contact.upload_contacts(upload_type='vcard',
                                           file_obj=file_obj, save=True)
        cs = Contact.filter_contacts_by_vcard(search_text='Aliya',
                                              search_params=[('fn')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='Aliya',
                                              search_params=[('fn',
                                                              'icontains')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='666',
                                              search_params=[('tel__value',
                                                              'icontains')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='666',
                                              search_params=[('tel__value',
                                                              'icontains'),
                                                             ('fn')])
        self.assertEqual(len(cs), 0)

    # def test_get_contacts_by_last_activity_date_without_activities(self):
    #     contacts = Contact.get_contacts_by_last_activity_date(user_id=1)
    #     self.assertEqual(len(contacts), 0)

    def test_get_contacts_by_last_activity_date(self):
        user_id = 1
        self.contact1.assign_user(user_id)

        response = Contact.get_contacts_by_last_activity_date(user_id)
        self.assertEqual(list(response.all()), [self.contact1])

        response = Contact.get_contacts_by_last_activity_date(user_id, True)
        self.assertIsInstance(response, tuple)
        self.assertEqual(list(response[0].all()), [self.contact1])
        self.assertEqual(list(response[1].values_list('pk', flat=True)),
                         [1, 2, 6, 3, 4, 5, 7])
        self.assertIsInstance(response[2], dict)
        self.assertEqual(response[2], {1: [1, 2, 6, 3, 4, 5, 7]})


class ActivityTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'feedbacks.json',
                'mentions.json']

    def setUp(self):
        super(ActivityTestCase, self).setUp()
        self.activity1 = Activity.objects.get(id=1)
        self.salescycle1 = SalesCycle.objects.get(id=1)

    def test_get_activities_by_contact(self):
        c = Contact.objects.get(id=1)
        a = Activity.objects.get(id=1)
        self.assertEqual(len(Activity.objects.filter(
                         sales_cycle__contact_id=c.id)),
                         len(a.get_activities_by_contact(c.id)))

    def test_set_feedback(self):
        self.assertNotEqual(0, len(Activity.objects.filter(sales_cycle_id=1)))
        self.assertNotEqual(0, len(Feedback.objects.all()))
        a = Activity(title='t6', description='d6', date_created=timezone.now(),
                     sales_cycle_id=1, owner_id=1)
        a.save()
        self.assertEqual(a, Activity.objects.get(id=a.id))
        self.assertEqual(0, len(Feedback.objects.filter(id=a.id)))
        f = Feedback(feedback='feedback8', status="W",
                     date_created=timezone.now(), date_edited=timezone.now(),
                     activity=a, owner_id=1)
        f.save()
        self.assertEqual(f, Feedback.objects.get(id=f.id))

        a.set_feedback(f, False)
        b = Activity.objects.last()
        self.assertEqual(b.feedback, f)
        a.set_feedback(f, True)
        a = Activity.objects.get(pk=a.pk)
        self.assertEqual(a.feedback, f)

    def test_get_activities_by_salescycle(self):
        all_activities = self.salescycle1.rel_activities.all()
        activities = Activity.get_activities_by_salescycle(1, 0, 0)
        if (len(all_activities) == len(activities)):
            self.assertEqual(len(set(all_activities).intersection(activities)),
                             len(activities))
        else:
            return False

    def test_get_mentioned_activities_of(self):
        user_ids = (1, 2)
        self.assertEqual(len(set(self.activity1.mentions.all())), 1)
        self.assertEqual(
            len(set(Activity.get_mentioned_activities_of(user_ids))), 4)

    def test_get_activity_details(self):
        for include_sc in [True, False]:
            for include_m in [True, False]:
                for include_c in [True, False]:
                    activity = Activity.get_activity_details(
                        self.activity1.id,
                        include_sales_cycle=True,
                        include_mentioned_users=True,
                        include_comments=True)

                    activity = Activity.get_activity_details(
                        self.activity1.id,
                        include_sales_cycle=include_sc,
                        include_mentioned_users=include_m,
                        include_comments=include_c)
                    self.assertTrue('activity' in activity)
                    details = activity['activity']
                    self.assertEqual(details['object'], self.activity1)

                    self.assertEqual('sales_cycle' in details, include_sc)
                    if include_sc:
                        self.assertEqual(details['sales_cycle'].__class__,
                                         SalesCycle().__class__)
                        self.assertEqual(details['sales_cycle'],
                                         self.activity1.sales_cycle)

                    self.assertEqual('mentioned_users' in details, include_m)
                    if include_m:
                        self.assertEqual(list(details['mentioned_users']),
                                         list(self.activity1.mentions.all()))

                    self.assertEqual('comments' in details, include_c)
                    if include_c:
                        self.assertQuerysetEqual(details['comments'],
                                                 self.activity1.comments.all())

    def test_get_number_of_activities_by_day(self):
        user_id = 1
        user_activities = Activity.objects.filter(owner=user_id)\
            .order_by('date_created')
        from_dt = user_activities.first().date_created
        to_dt = user_activities.last().date_created
        self.assertTrue(from_dt < to_dt)
        owned_data = Activity.get_number_of_activities_by_day(user_id,
                                                              from_dt,
                                                              to_dt)
        self.assertEqual(sum(owned_data.values()), user_activities.count())
        self.assertEqual(owned_data, {'2014-09-15': 1, '2014-09-11': 1,
                         '2014-09-13': 1, '2014-09-12': 2})


class MentionTestCase(TestCase):
    fixtures = ['mentions.json']

    def setUp(self):
        super(MentionTestCase, self).setUp()

    def test_get_all_mentions_of(self):
        user_id = 1
        self.assertEqual(list(Mention.get_all_mentions_of(user_id)),
                         list(Mention.objects.filter(user_id=user_id)))

    def test_build_new__without_save(self):
        user_id = 1
        before = Mention.get_all_mentions_of(user_id).count()
        self.assertEqual(Mention.build_new(user_id, Activity, 1).
                         __class__, Mention)
        self.assertEqual(Mention.get_all_mentions_of(user_id).count(), before)

    def test_build_new(self):
        user_id = 1
        before = Mention.get_all_mentions_of(user_id).count()
        self.assertEqual(Mention.build_new(user_id, Activity, 1, True).pk,
                         Mention.objects.last().pk)
        self.assertEqual(Mention.get_all_mentions_of(user_id).count(),
                         before + 1)


class CommentTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'mentions.json']

    def setUp(self):
        super(CommentTestCase, self).setUp()

    def test_build_new_without_save(self):
        user_id = 1
        before = Comment.get_comments_by_context(1, Activity).count()

        self.assertEqual(Comment.build_new(user_id, Activity, 1).
                         __class__, Comment)
        self.assertEqual(Comment.get_comments_by_context(1, Activity).count(),
                         before)

    def test_build_new(self):
        user_id = 1
        before = Comment.get_comments_by_context(1, Activity).count()
        comment = Comment.build_new(user_id, Activity, 1, True)
        received_comments = Comment.get_comments_by_context(1, Activity)

        self.assertEqual(received_comments.count(), before + 1)
        self.assertTrue(comment.id in
                        received_comments.values_list('pk', flat=True))

    def test_get_comments_by_context(self):
        activity1 = Activity.objects.get(pk=1)

        self.assertEqual(Comment.get_comments_by_context(1, Activity, 1, 0)
                         .count(), activity1.comments.count())
        self.assertEqual(Comment.get_comments_by_context(1, Activity, 1, 1)
                         .count(), 0)


class SalesCycleTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'mentions.json',
                'products.json', 'values.json']

    def setUp(self):
        super(SalesCycleTestCase, self).setUp()
        self.sc1 = SalesCycle.objects.get(pk=1)

    def get_sc(self, pk):
        return SalesCycle.objects.get(pk=pk)

    def test_add_mention(self):
        self.assertEqual(len(self.sc1.mentions.all()), 0)
        self.sc1.add_mention([1, 2])
        self.assertEqual(len(self.get_sc(pk=1).mentions.all()), 2)

    def test_assign_user_without_save(self):
        prev_owner_id = self.sc1.owner_id
        self.assertNotEqual(prev_owner_id, 2)
        self.assertTrue(self.sc1.assign_user(2, False))
        self.assertEqual(self.get_sc(1).owner_id, prev_owner_id)

    def test_assign_user_with_save(self):
        self.assertEqual(self.sc1.owner_id, 1)
        self.assertTrue(self.sc1.assign_user(2, True))
        self.assertEqual(self.get_sc(1).owner_id, 2)

    def test_get_activities(self):
        self.assertEqual(
            list(self.sc1.get_activities().values_list('id', flat=True)),
            [4, 3, 2, 1])

    def test_add_product(self):
        count = len(self.sc1.products.all())
        self.assertTrue(self.sc1.add_product(2))
        self.assertEqual(len(self.get_sc(self.sc1.pk).products.all()),
                         count + 1)

    def test_set_result_without_save(self):
        self.assertEqual(self.sc1.real_value_id, 1)
        value_obj = Value.objects.get(pk=2)
        self.assertIsNone(self.sc1.set_result(value_obj))
        self.assertEqual(self.get_sc(pk=1).real_value_id, 1)

    def test_add_followers(self):
        self.assertEqual(list(self.sc1.followers.all()), [])
        self.assertEqual(self.sc1.add_followers([1]), [True])
        self.assertEqual(self.sc1.followers.first().pk, 1)

    def test_upd_lst_activity_on_create(self):
        activity = Activity(sales_cycle_id=1, owner_id=1)
        activity.save()
        self.assertEqual(self.get_sc(pk=1).latest_activity.pk, activity.pk)

    def test_get_salescycles_by_last_activity_date(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(user_id)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)), [3, 2, 1])
        self.assertEqual(list(ret[1].values_list('pk', flat=True)),
                         range(1, 8))
        self.assertItemsEqual(ret[2], {1: [1, 3], 2: [2], 3: []})

    def test_get_salescycles_by_last_activity_date_with_mentioned(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(user_id,
                                                               mentioned=True)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)),
                         [3, 2, 1, 4])
        self.assertEqual(list(ret[1].values_list('pk', flat=True)),
                         range(1, 8))
        self.assertItemsEqual(ret[2], {1: [1, 3], 2: [2], 3: [], 4: []})

    def test_get_salescycles_by_last_activity_date_only_mentioned(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(user_id,
                                                               owned=False,
                                                               mentioned=True)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)), [4])
        self.assertEqual(list(ret[1].values_list('pk', flat=True)), [])
        self.assertItemsEqual(ret[2], {4: []})

    def test_get_salescycles_by_last_activity_date_only_followed(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(user_id,
                                                               owned=False,
                                                               mentioned=False,
                                                               followed=True)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)), [3])
        self.assertEqual(list(ret[1].values_list('pk', flat=True)), [7])
        self.assertItemsEqual(ret[2], {3: [7]})

    def test_get_salescycles_by_last_activity_date_without_user_id(self):
        user_id = 5
        try:
            CRMUser.objects.get(pk=user_id)
        except CRMUser.DoesNotExist:
            raised = True
        else:
            raised = False
        finally:
            self.assertTrue(raised)

        try:
            SalesCycle.get_salescycles_by_last_activity_date(user_id)
        except CRMUser.DoesNotExist:
            raised = True
        else:
            raised = False
        finally:
            self.assertTrue(raised)

    def test_get_salescycles_by_contact(self):
        ret = SalesCycle.get_salescycles_by_contact(1)
        self.assertEqual(list(ret.values_list('pk', flat=True)), [1, 2, 3, 4])


class ResourceTestMixin(object):
    fixtures = ['companies.json', 'services.json', 'users.json',
                'subscriptions.json',
                'crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'products.json', 'values.json',
                'activities.json', 'mentions.json', 'comments.json']

    def get_user(self):
        from alm_user.models import User
        self.user = User.objects.get(pk=1)
        self.user_password = '123'

    def get_credentials(self):
        self.get_user()
        post_data = {
            'email': self.user.email,
            'password': self.user_password
        }
        self.api_path_user_session = '/api/v1/user_session/'

        # create session
        self.api_client.post(self.api_path_user_session, format='json',
                             data=post_data)


class UserSessionResourceTest(ResourceTestMixin, ResourceTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()

        self.api_path_user_session = '/api/v1/user_session/'

    def test_get_detail_valid_json(self):
        resp = self.api_client.get(
            self.api_path_user_session, format='json', HTTP_HOST='localhost')
        self.assertValidJSONResponse(resp)

    def test_get_detail_without_session(self):
        resp = self.api_client.get(
            self.api_path_user_session, format='json', HTTP_HOST='localhost')
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_create_session(self):
        self.get_user()
        post_data = {
            'email': self.user.email,
            'password': self.user_password
        }

        # create session
        resp = self.api_client.post(
            self.api_path_user_session, format='json', data=post_data)
        self.assertHttpCreated(resp)

        # get_detail to check session was created
        resp = self.api_client.get(
            self.api_path_user_session, format='json', HTTP_HOST='localhost')
        des_resp = self.deserialize(resp)
        self.assertEqual(len(des_resp['objects']), 1)

        session_user = des_resp['objects'][0]['user']
        self.assertEqual(session_user['id'], self.user.id)

    def test_delete_session(self):
        # create session
        self.get_credentials()

        # get session_key by get_detail
        resp = self.api_client.get(
            self.api_path_user_session, format='json', HTTP_HOST='localhost')
        session_key = self.deserialize(resp)['objects'][0]['id']

        self.api_client.delete(self.api_path_user_session+'%s/' % session_key,
                               format='json', HTTP_HOST='localhost')

        # get_detail to check session was deleted
        resp = self.api_client.get(
            self.api_path_user_session, format='json', HTTP_HOST='localhost')
        des_resp = self.deserialize(resp)
        # find session with deleted session_key
        prev_obj = filter(lambda s: s['id'] == session_key,
                          des_resp['objects'])
        self.assertEqual(len(prev_obj), 0)


class SalesCycleResourceTest(ResourceTestMixin, ResourceTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_sales_cycle = '/api/v1/sales_cycle/'

        self.get_resp = lambda path: self.api_client.get(
            self.api_path_sales_cycle + path,
            format='json',
            HTTP_HOST='localhost')
        self.get_des_res = lambda path: self.deserialize(self.get_resp(path))

        self.sales_cycle = SalesCycle.objects.first()

    # def test_get_list_unauthorzied(self):
    #     self.assertHttpUnauthorized(self.api_client.get(
    #         self.api_path_sales_cycle, format='json'))

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_resp(''))

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_des_res('')['meta']['total_count'] > 0)

    # def test_get_detail_unauthorzied(self):
    #     self.assertHttpUnauthorized(self.api_client.get(
    #         self.api_path_sales_cycle + '1/', format='json'))

    def test_get_detail_json(self):
        self.assertEqual(
            self.get_des_res(str(self.sales_cycle.pk)+'/')['title'],
            self.sales_cycle.title
            )

    def test_create_sales_cycle(self):
        post_data = {
            'title': 'new SalesCycle from test_unit',
            'contact': {'pk': Contact.objects.last()},
            'activities': []
        }

        count = SalesCycle.objects.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_sales_cycle, format='json', data=post_data))
        sales_cycle = SalesCycle.objects.last()
        # verify that new one has been added.
        self.assertEqual(SalesCycle.objects.count(), count + 1)
        # verify that subscription_id was set
        self.assertIsInstance(sales_cycle.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(sales_cycle.owner, CRMUser)
        self.assertEqual(
            sales_cycle.owner,
            self.user.get_subscr_user(sales_cycle.subscription_id)
            )

    def test_create_sales_cycle_with_activity(self):
        post_data = {
            'title': 'new SalesCycle with one Activity',
            'contact': {'pk': Contact.objects.last()},
            'activities': [{
                'title': 'new_sc_a1',
                'description': 'new sales_cycle\'s activity'
            }]
        }

        count = SalesCycle.objects.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_sales_cycle, format='json', data=post_data))
        sales_cycle = SalesCycle.objects.last()
        # verify that new one sales_cycle has been added.
        self.assertEqual(SalesCycle.objects.count(), count + 1)
        # verify that added with one activity
        self.assertEqual(sales_cycle.rel_activities.count(), 1)

    @skipIf(True, "Tastypie need overwrite save_m2m() to able create with M2M")
    def test_create_sales_cycle_with_product(self):
        post_data = {
            'name': 'new SalesCycle with one Product',
            'contact': {'pk': Contact.objects.last()},
            'products': [{
                'name': 'p1',
                'description': 'new product p1',
                'price': 100
            }]
        }

        count = SalesCycle.objects.count()
        # self.assertHttpCreated()
        print self.api_client.post(
            self.api_path_sales_cycle, format='json', data=post_data)

        sales_cycle = SalesCycle.objects.last()
        # verify that new one sales_cycle has been added.
        self.assertEqual(SalesCycle.objects.count(), count + 1)
        # verify that added with one activity
        self.assertEqual(sales_cycle.products.count(), 1)

    def test_delete_sales_cycle(self):
        count = SalesCycle.objects.count()
        sales_cycle = SalesCycle.objects.last()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_sales_cycle + '%s/' % sales_cycle.pk, format='json'))
        # verify that one sales_cycle has been deleted.
        self.assertEqual(SalesCycle.objects.count(), count - 1)


class ActivityResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_activity = '/api/v1/activity/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_activity,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_activity+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.activity = Activity.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        resp_activity = self.get_detail_des(self.activity.pk)

        self.assertEqual(resp_activity['title'], self.activity.title)

        self.assertTrue(len(resp_activity['comments']) > 0)
        self.assertEqual(len(self.activity.comments.all()),
                         len(resp_activity['comments']))

        self.assertTrue(len(resp_activity['mentions']) > 0)
        self.assertEqual(len(self.activity.mentions.all()),
                         len(resp_activity['mentions']))

    def test_create_activity(self):
        sales_cycle = SalesCycle.objects.last()
        post_data = {
            'title': 'new activity1',
            'description': 'new activity by test_unit',
            'sales_cycle': {'pk': sales_cycle.pk}
        }

        count = sales_cycle.rel_activities.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_activity, format='json', data=post_data))
        activity = sales_cycle.rel_activities.last()
        # verify that new one has been added.
        self.assertEqual(sales_cycle.rel_activities.count(), count + 1)
        # verify that subscription_id was set
        self.assertIsInstance(activity.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(activity.owner, CRMUser)
        self.assertEqual(
            activity.owner,
            self.user.get_subscr_user(activity.subscription_id)
            )

    def test_create_activity_mentions(self):
        sales_cycle = SalesCycle.objects.last()
        post_data = {
            'title': 'new activity1',
            'description': 'new activity by test_unit',
            'sales_cycle': {'pk': sales_cycle.pk},
            'mention_user_ids': [1, 2]
        }

        count_activities = sales_cycle.rel_activities.count()
        count_mentions = Mention.objects.count()

        self.assertHttpCreated(self.api_client.post(
            self.api_path_activity, format='json', data=post_data))

        self.assertEqual(count_activities + 1,
                         sales_cycle.rel_activities.count())
        self.assertEqual(count_mentions + 2, Mention.objects.count())

    def test_delete_activity(self):
        sales_cycle = self.activity.sales_cycle
        count = sales_cycle.rel_activities.count()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_activity + '%s/' % self.activity.pk, format='json'))
        # verify that one sales_cycle has been deleted.
        self.assertEqual(sales_cycle.rel_activities.count(), count - 1)


class ProductResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_product = '/api/v1/product/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_product,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_product+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.product = Product.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.product.pk)['name'],
            self.product.name
            )

    def test_create_product(self):
        sales_cycle = SalesCycle.objects.last()
        post_data = {
            'name': 'new product',
            'description': 'new product by test_unit',
            'price': 100,
            'sales_cycles': [{'pk': sales_cycle.pk}]
        }

        count = sales_cycle.products.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_product, format='json', data=post_data))
        product = sales_cycle.products.last()
        # verify that new one has been added.
        self.assertEqual(sales_cycle.products.count(), count + 1)
        # verify that subscription_id was set
        self.assertIsInstance(product.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(product.owner, CRMUser)
        self.assertEqual(
            product.owner,
            self.user.get_subscr_user(product.subscription_id)
            )

    def test_delete_product(self):
        sales_cycle = self.product.sales_cycles.first()
        count = sales_cycle.products.count()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_product + '%s/' % self.product.pk, format='json'))
        # verify that one sales_cycle has been deleted.
        self.assertEqual(sales_cycle.products.count(), count - 1)

<<<<<<< HEAD
    def test_update_product_via_put(self):
        # get exist product data
        p = Product.objects.first()
        product_data = self.get_detail_des(p.pk)
        # update it
        t = '_UPDATED!'
        product_data['name'] += t
        # PUT it
        self.api_client.put(self.api_path_product + '%s/' % (p.pk),
                            format='json', data=product_data)
        # check
        self.assertEqual(self.get_detail_des(p.pk)['name'], p.name + t)

    def test_update_product_via_patch(self):
        # get exist product data
        p = Product.objects.first()
        product_name = self.get_detail_des(p.pk)['name']
        # update it
        t = '_NAME_UPDATED!'
        product_name += t
        # PATCH it
        self.api_client.patch(self.api_path_product + '%s/' % (p.pk),
                              format='json', data={'name': product_name})
        # check
        self.assertEqual(self.get_detail_des(p.pk)['name'], product_name)


=======
>>>>>>> feature/tastypie_api_tests_nurlan
class ContactResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_contact = '/api/v1/contact/'
<<<<<<< HEAD
        self.api_path_contact_products_f = '/api/v1/contact/%s/products/'
        self.api_path_contact_activities_f = '/api/v1/contact/%s/activities/'
=======
>>>>>>> feature/tastypie_api_tests_nurlan

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_contact,
                                                 format='json',
                                                 HTTP_HOST='localhost')
<<<<<<< HEAD
        self.get_list_des = self.deserialize(self.get_list_resp)

=======

        self.get_list_des = self.deserialize(self.get_list_resp)

        #get list for cold base
        self.get_list_cold_base_resp = self.api_client.get(self.api_path_contact+'cold_base/', 
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        self.get_list_cold_base_des = self.deserialize(self.get_list_cold_base_resp)

        #get list for leads
        self.get_list_leads_resp = self.api_client.get(self.api_path_contact+'leads/', 
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        self.get_list_leads_des = self.deserialize(self.get_list_leads_resp)

        #get list for recent contacts
        self.get_list_recent_resp = self.api_client.get(self.api_path_contact+'recent/', 
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        self.get_list_recent_des = self.deserialize(self.get_list_recent_resp)

        #get list for assign contact
        self.get_list_assign_contact_resp = self.api_client.get(self.api_path_contact+'assign_contact/', 
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        self.get_list_assign_contact_des = self.deserialize(self.get_list_assign_contact_resp)


>>>>>>> feature/tastypie_api_tests_nurlan
        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_contact+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
<<<<<<< HEAD
=======

>>>>>>> feature/tastypie_api_tests_nurlan
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.contact = Contact.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)
<<<<<<< HEAD

    def test_get_products(self):
        resp = self.api_client.get(
            self.api_path_contact_products_f % (self.contact.pk),
            format='json',
            HTTP_HOST='localhost'
            )
        self.assertEqual(len(self.deserialize(resp)['objects']),
                         len(Contact.get_contact_products(self.contact.pk)))

    def test_get_activities_with_embedded_comments(self):
        resp = self.api_client.get(
            self.api_path_contact_activities_f % (self.contact.pk),
            format='json',
            HTTP_HOST='localhost'
            )
        activites = self.deserialize(resp)['objects']

        self.assertEqual(len(activites),
                         len(Contact.get_contact_activities(self.contact.pk)))

        # exists at least one comment from activities
        self.assertTrue(sum(len(a['comments']) for a in activites) > 0)

        for a in activites:
            self.assertEqual(
                len(Activity.objects.get(pk=a['id']).comments.all()),
                len(a['comments'])
                )
=======
        self.assertValidJSONResponse(self.get_list_cold_base_resp)
        self.assertValidJSONResponse(self.get_list_leads_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.contact.pk)['id'],
            self.contact.id
            )

    def test_create_contact(self):
        post_data = {
            'sales_cycles':[{'pk': SalesCycle.objects.first()}],
            'status': 1,
            'tp': 'user',
        }

        count = Contact.objects.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_contact, format='json', data=post_data))
        # verify that new one has been added.
        self.assertEqual(Contact.objects.count(), count + 1)

    @skipIf(True, "IntegrityError")
    def test_delete_contact(self):
        count = Contact.objects.count()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_contact + '%s/' % self.contact.pk, format='json'))
        # verify that one contact been deleted.
        self.assertEqual(Contact.objects.count(), count - 1)

    
    def test_get_last_contacted(self):
        recent = Contact.get_contacts_by_last_activity_date(1)
        self.assertEqual(
            len(self.get_list_recent_des['objects']),
            len(recent)
            )

    def test_get_cold_base(self):
        cold_base = Contact.get_cold_base()
        self.assertEqual(
            len(self.get_list_cold_base_des['objects']),
            len(cold_base)
            )

        
    def test_get_leads(self):
        STATUS_LEAD = 1
        leads = Contact.get_contacts_by_status(STATUS_LEAD)
        self.assertEqual(
            len(self.get_list_leads_des['objects']),
            len(leads)
            )        


    def test_assign_contact(self):
        self.contact.assignees.add(CRMUser.objects.last())
        post_data = {
            'user_id': 1,
            'contact_id': 1
        }
        count = self.contact.assignees.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'assign_contact/?user_id=1&contact_id=1'))

        self.assertEqual(self.contact.assignees.count(), count)

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'assign_contact/?user_id=2&contact_id=1'))

        self.assertEqual(self.contact.assignees.count(), count+1)

    # def test_assign_contacts(self, request, **kwargs):

   	# def test_search(self, request, **kwargs):

    # def test_share_contact(self, request, **kwargs):

    # def test_share_contacts(self, request, **kwargs):

>>>>>>> feature/tastypie_api_tests_nurlan
