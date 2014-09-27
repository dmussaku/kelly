import os
from django.test import TestCase
from django.utils import timezone
from alm_crm.models import Contact, CRMUser, Activity, SalesCycle, Feedback,\
    Mention, Feedback, Value, Comment
from alm_vcard.models import VCard


class ContactTestCase(TestCase):
    fixtures = ['crmusers.json', 'contacts.json', 'salescycles.json',
                'activities.json', 'feedbacks.json']

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

    def test_change_status(self):
        self.assertEqual(self.contact1.status, 0)
        self.contact1.change_status(1)
        self.assertEqual(self.contact1.status, 1)

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
        contacts = Contact.upload_contacts('vcard', file_obj, True)
        cs = Contact.filter_contacts_by_vcard(search_text='Aliya',
                                              search_params=[('fn')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='Aliya',
                                              search_params=[('fn', 'icontains')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='666',
                                              search_params=[('tel__value', 'icontains')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='666',
                                              search_params=[('tel__value', 'icontains'),
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
    fixtures = ['crmusers.json', 'contacts.json', 'salescycles.json',
                'activities.json', 'feedbacks.json', 'mentions.json']

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
                     sales_cycle_id=1, author_id=1)
        a.save()
        self.assertEqual(a, Activity.objects.get(id=a.id))
        self.assertEqual(0, len(Feedback.objects.filter(id=a.id)))
        f = Feedback(feedback='feedback8', status="W",
                     date_created=timezone.now(), date_edited=timezone.now(),
                     activity=a)
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
        user_ids = [1, 2]
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
        user_activities = Activity.objects.filter(author=user_id)\
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
    fixtures = ['crmusers.json', 'contacts.json', 'salescycles.json',
                'activities.json', 'mentions.json']

    def setUp(self):
        super(CommentTestCase, self).setUp()

    def test_build_new__without_save(self):
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
    fixtures = ['crmusers.json', 'contacts.json', 'salescycles.json',
                'activities.json', 'mentions.json', 'products.json',
                'values.json']

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
        self.assertEqual(len(self.sc1.products.all()), 0)
        self.assertTrue(self.sc1.add_product(1))
        self.assertEqual(len(self.get_sc(1).products.all()), 1)

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
        activity = Activity(sales_cycle_id=1, author_id=1)
        activity.save()
        self.assertEqual(self.get_sc(pk=1).latest_activity.pk, activity.pk)

    def test_get_salescycles_by_last_activity_date(self):
        ret = SalesCycle.get_salescycles_by_last_activity_date(1)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)), [3, 2, 1])
        self.assertEqual(list(ret[1].values_list('pk', flat=True)),
                         range(1, 8))
        self.assertItemsEqual(ret[2], {1: [1, 3], 2: [2], 3: []})

    def test_get_salescycles_by_contact(self):
        ret = SalesCycle.get_salescycles_by_contact(1)
        self.assertEqual(list(ret.values_list('pk', flat=True)), [1, 2, 3, 4])
