import os
from django.test import TestCase
from django.utils import timezone
from alm_crm.models import Contact, Activity, SalesCycle, Feedback, Mention,\
    Comment
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

    def test_upload_contacts_by_vcard(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/brown.vcf')
        file_obj = open(file_path, "r").read()
        contact = Contact._upload_contacts_by_vcard(file_obj)
        self.assertEqual(contact.__class__, Contact)
        self.assertEqual(contact.vcard.__class__, VCard)
        self.assertNotEqual(contact.name, "Unknown")

    def test_upload_contacts_by_vcard_2(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/aliya.vcf')
        file_obj = open(file_path, "r").read()
        contact = Contact._upload_contacts_by_vcard(file_obj)
        self.assertEqual(contact.__class__, Contact)
        self.assertEqual(contact.vcard.__class__, VCard)
        addr = list(contact.vcard.adr_set.all())
        self.assertEqual(len(addr), 2)
        self.assertNotEqual(contact.name, "Unknown")

    def test_get_contacts_by_last_activity_date(self):
        pass


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
        a = Activity(title='t6', description='d6', when=timezone.now(),
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
            len(set(Activity.get_mentioned_activities_of(user_ids))), 1)

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
            .order_by('when')
        from_dt = user_activities.first().when
        to_dt = user_activities.last().when
        self.assertTrue(from_dt < to_dt)
        owned_data = Activity.get_number_of_activities_by_day(user_id,
                                                              from_dt,
                                                              to_dt)
        self.assertEqual(sum(owned_data.values()), user_activities.count())
        self.assertEqual(owned_data.values(), [1, 1, 2])


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
        self.assertEqual(Mention.build_new(user_id, Activity, 1, True).
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
    fixtures = ['mentions.json']

    def setUp(self):
        super(CommentTestCase, self).setUp()

    def test_build_new__without_save(self):
        user_id = 1
        before = Comment.get_comments_by_context(1, Mention).count()
        self.assertEqual(Comment.build_new(user_id, Mention, 1, True).
                         __class__, Mention)
        self.assertEqual(Comment.get_comments_by_context(1, Mention).count(),
                         before)

    def test_build_new(self):
        user_id = 1
        before = Comment.get_comments_by_context(1, Mention).count()
        self.assertEqual(Comment.build_new(user_id, Mention, 1, True).pk,
                         Comment.get_comments_by_context(1, Mention).last().pk)
        self.assertEqual(Comment.get_comments_by_context(1, Mention).count(),
                         before + 1)

    def test_get_comments_by_context(self):
        self.assertEqual(Comment.get_comments_by_context(1, Mention, 1, 0)
                         .count(), 1)
        self.assertEqual(Comment.get_comments_by_context(1, Mention, 1, 1)
                         .count(), 0)
