# -*- coding: utf-8 -*-
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
    SalesCycleLogEntry,
    Milestone,
    Product,
    Mention,
    Feedback,
    Value,
    Comment,
    Share,
    ContactList,
    SalesCycleProductStat,
    Filter,
    HashTag,
    HashTagReference,
    )
from alm_vcard.models import VCard, Tel, Email, Org
from alm_user.models import User
from almanet.models import Subscription, Service
from alm_crm.models import GLOBAL_CYCLE_TITLE
from alm_company.models import Company


class CRMUserTestCase(TestCase):
    fixtures = ['crmusers.json', 'users.json']

    def setUp(self):
        super(CRMUserTestCase, self).setUp()
        self.crmuser = CRMUser.objects.first()

    def test_unicode(self):
        self.assertEqual(str(self.crmuser), 'Bruce Wayne')

    def test_get_billing_user(self):
        self.assertEqual(self.crmuser.get_billing_user(),
                         User.objects.get(pk=self.crmuser.user_id))

    def test_set_supervisor(self):
        self.crmuser.set_supervisor()
        self.assertTrue(self.crmuser.is_supervisor)

    def test_unset_supervisor(self):
        self.crmuser.unset_supervisor()
        self.assertFalse(self.crmuser.is_supervisor)

    def test_get_crmusers(self):
        self.assertEqual(CRMUser.get_crmusers(self.crmuser.subscription_id).last(), 
                                                            CRMUser.objects.last())
        user = User.objects.first()
        get_with_users = CRMUser.get_crmusers(subscription_id = self.crmuser.subscription_id,
                                                with_users=True)
        self.assertTrue(user in get_with_users[1])


class ContactTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'feedbacks.json',
                'emails.json', 'organizations.json', 'users.json',
                'vcards.json']

    def setUp(self):
        super(ContactTestCase, self).setUp()
        self.contact1 = Contact.objects.get(pk=1)
        self.crmuser = self.contact1.owner
        self.crm_subscr_id = CRMUser.get_subscription_id(self.crmuser.id)

    def test_get_contacts_by_status(self):
        contacts = Contact.get_contacts_by_status(self.crm_subscr_id, status=1)
        self.assertEqual(len(contacts), 2)

    def test_get_cold_base(self):
        cold_contacts = Contact.get_cold_base(self.crm_subscr_id)
        self.assertEqual(len(cold_contacts), 1)

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
        # amount_before_import = SalesCycle.objects.all().count()
        file_obj = open(file_path, "r").read()
        contact = Contact.upload_contacts(upload_type='vcard',
                                          file_obj=file_obj,
                                          save = True)
        # amount_after_import = SalesCycle.objects.all().count()
        # self.assertEqual(amount_after_import, amount_before_import+1)
        # self.assertTrue(c.sales_cycles.first().title == GLOBAL_CYCLE_TITLE for c in contacts)
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
        cs = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                              search_text='Akerke Akerke',
                                              search_params=[('fn')],
                                              order_by=[])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                              search_text='Akerke',
                                              search_params=[('fn', 'icontains')],
                                              order_by=[])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                              search_text='359',
                                              search_params=[('tel__value', 'icontains')],
                                              order_by=[])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                              search_text='359',
                                              search_params=[('fn', 'icontains')],
                                              order_by=[])
        self.assertEqual(len(cs), 0)

    def test_get_contacts_by_last_activity_date_without_activities(self):
        contacts = Contact.get_contacts_by_last_activity_date(subscription_id=1)
        self.assertEqual(len(contacts), 0)

    def test_get_contacts_by_last_activity_date(self):
        contacts = Contact.get_contacts_by_last_activity_date(self.crm_subscr_id,
                                                              all=True)
        subscr_contacts = Contact.objects.filter(subscription_id=self.crm_subscr_id)
        self.assertEqual(contacts.count(), subscr_contacts.count())

    def test_export_to(self):
        self.assertFalse(self.contact1.export_to(tp='doc'))
        vcard = self.contact1.export_to(tp='vcard')
        tel = 'TEL;TYPE=CELL:%s' % self.contact1.tel()
        self.assertTrue(tel in vcard)

    def test_properties(self):
        contact2 = Contact.objects.get(pk=2)
        contact2.vcard = None
        self.assertEqual(self.contact1.tel(), Tel.objects.get(vcard=self.contact1.vcard).value)
        self.assertEqual(self.contact1.mobile(), Tel.objects.get(vcard=self.contact1.vcard).value)
        self.assertEqual(self.contact1.email(), Email.objects.get(vcard=self.contact1.vcard).value)
        self.assertEqual(self.contact1.company(), Org.objects.get(vcard=self.contact1.vcard).name)
        self.assertTrue(contact2.is_new())
        self.assertTrue(self.contact1.is_lead())
        self.assertTrue(Contact.objects.get(pk=3).is_opportunity())
        self.assertTrue(Contact.objects.get(pk=4).is_client())

    def test_to_html(self):
        html = self.contact1.to_html()
        email = '%s<br />' % self.contact1.email()
        self.assertTrue(email in html)

    def test_add_mentions(self):
        count = Mention.objects.all().count()
        self.contact1.add_mention(user_ids=1)
        self.assertEqual(Mention.objects.all().count(), count+1)
        self.assertEqual(self.contact1.mentions.get(pk=1),
                         Mention.objects.last())

    def test_share_contacts(self):
        share_to = CRMUser.objects.get(id=1)
        share_from = CRMUser.objects.get(id=2)
        shares = Contact.share_contacts(share_from=share_from,
                                        share_to=share_to,
                                        contact_ids=[])
        self.assertFalse(shares)

    def test_get_contact_detail(self):
        self.assertEqual(Contact.get_contact_detail(1), self.contact1)
        self.assertEqual(Contact.get_contact_detail(1, True), self.contact1)

    def test_import_from_vcard(self):
        count = Contact.objects.all().count()
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/nurlan.vcf')
        amount_before_import = SalesCycle.objects.all().count()
        contacts = Contact.import_from_vcard(raw_vcard=open(file_path, "r"),
                                                creator=CRMUser.objects.first())
        amount_after_import = SalesCycle.objects.all().count()

        contact1 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Aslan',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        contact2 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Serik',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        contact3 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Almat',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        contact4 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Mukatayev',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        self.assertEqual(amount_after_import, amount_before_import+3)
        self.assertTrue(c.sales_cycles.first().title == GLOBAL_CYCLE_TITLE for c in contacts)
        self.assertEqual(len(Contact.objects.all()), count+3)
        self.assertEqual(len(contact4), 3)
        self.assertTrue(contact1.first() in Contact.objects.all())
        self.assertTrue(contact2.first() in Contact.objects.all())
        self.assertTrue(contact3.first() in Contact.objects.all())

    def test_get_tp(self):
        tp_unicode = unicode(self.contact1.get_tp())
        contact_tp = self.contact1.tp + ' type'
        self.assertEqual(tp_unicode, contact_tp)


class ValueTestCase(TestCase):
    fixtures = ['values.json']

    def setUp(self):
        super(ValueTestCase, self).setUp()
        self.value = Value.objects.get(pk=1)

    def test_unicode(self):
        value = Value(salary='monthly', amount = 100000, currency ='KZT')
        self.assertEqual(value.__unicode__(), '100000 KZT monthly')


class ProductTestCase(TestCase):
    fixtures = ['products.json', 'crmusers.json']

    def setUp(self):
        super(ProductTestCase, self).setUp()
        self.product = Product.objects.get(pk=1)
        self.crm_subscr_id = 1

    def test_unicode(self):
        self.assertEqual(self.product.__unicode__(), 'p1')

    def test_get_products(self):
        self.assertEqual(len(Product.objects.all()),
                         len(Product.get_products(self.crm_subscr_id)))


class ActivityTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'feedbacks.json', 'emails.json',
                 'organizations.json', 'users.json', 'vcards.json', 'comments.json', 'mentions.json']

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
        f = Feedback(feedback='feedback8', status=Feedback.WAITING,
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
        activities = Activity.get_activities_by_salescycle(1)
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
                    # if include_c:
                    #     self.assertQuerysetEqual(details['comments'].order_by('id'),
                    #                              self.activity1.comments.all())

    def test_get_number_of_activities_by_day(self):
        user_id = 2
        user_activities = Activity.objects.filter(owner=user_id)\
            .order_by('date_created')
        from_dt = user_activities.first().date_created
        to_dt = user_activities.last().date_created
        self.assertTrue(from_dt < to_dt)
        owned_data = Activity.get_number_of_activities_by_day(user_id,
                                                              from_dt,
                                                              to_dt)
        self.assertEqual(sum(owned_data.values()), user_activities.count())
        self.assertEqual(owned_data, {'2014-12-30': 3, '2014-11-24': 3})
        


    def test_unicode(self):
        self.assertEqual(self.activity1.__unicode__(), self.activity1.description)


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
                'salescycles.json', 'activities.json', 'mentions.json',
                'comments.json']

    def setUp(self):
        super(CommentTestCase, self).setUp()
        self.comment = Comment.objects.first()

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

        self.assertEqual(Comment.get_comments_by_context(1, Activity)
                         .count(), activity1.comments.count())
        self.assertEqual(Comment.get_comments_by_context(1, Activity)
                         .count(), 30)

    def test_add_mention(self):
        count = self.comment.mentions.count()
        self.comment.add_mention(user_ids=[2,3,4])
        self.assertEqual(self.comment.mentions.count(), count+3)


class SalesCycleTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'mentions.json',
                'products.json', 'values.json', 'salescycle_product_stat.json', 
                'milestones.json', 'comments.json', 'sc_log_entry.json']

    def setUp(self):
        super(SalesCycleTestCase, self).setUp()
        self.sc1 = SalesCycle.objects.get(pk=1)
        self.crmusers = self.sc1.owner
        self.crm_subscr_id = 1

    def get_sc(self, pk):
        return SalesCycle.objects.get(pk=pk)

    def test_try_to_create_another_global_cycle(self):
        contact = Contact.objects.first()
        owner = contact.owner
        subscription_id = owner.subscription_id
        count = SalesCycle.objects.all().count()
        self.assertEqual(SalesCycle.create_globalcycle(**{'subscription_id': subscription_id,
                                                         'owner_id': owner.id,
                                                         'contact_id': contact.id}),
                        contact.sales_cycles.get(is_global=True))
        actual_count = SalesCycle.objects.all().count()
        expected_count = count
        self.assertEqual(actual_count, expected_count)

    def test_create_cycle_with_empty_title(self):
        title = ""
        description = "SalesCycle description"
        contact = Contact.objects.first()
        owner = contact.owner
        sales_cycle = SalesCycle(title = title, description=description, contact=contact, owner=owner)
        raised = False
        try:
            sales_cycle.save()
        except Exception:
            raised = True
        self.assertTrue(raised)


    def test_unicode(self):
        self.assertEqual(self.sc1.__unicode__(), '%s [%s %s]' % (self.sc1.title, self.sc1.contact, self.sc1.status))

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
            [2, 4, 6, 1, 3])

    def test_add_product(self):
        count = len(self.sc1.products.all())
        self.assertTrue(self.sc1.add_product(3))
        self.assertEqual(len(self.get_sc(self.sc1.pk).products.all()),
                         count + 1)

    def test_remove_product(self):
        count = len(self.sc1.products.all())
        self.assertTrue(self.sc1.remove_product(2))
        self.assertEqual(len(self.get_sc(self.sc1.pk).products.all()),
                         count - 1)

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
        ret = SalesCycle.get_salescycles_by_last_activity_date(self.crm_subscr_id,
                                                               user_id,
                                                               include_activities=True)
        self.assertEqual(sorted(list(ret[0].values_list('pk', flat=True))), [1, 2, 3, 4, 5])
        self.assertEqual(sorted(list(ret[1].values_list('pk', flat=True))), range(1, 7))
        self.assertItemsEqual(ret[2], {1: [1, 2, 3, 4, 5, 6], 2: [], 3: [], 4: [], 5: []})



    def test_get_salescycles_by_last_activity_date_with_mentioned(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(self.crm_subscr_id,
                                                               user_id,
                                                               mentioned=True,
                                                               include_activities=True)
        self.assertEqual(sorted(list(ret[0].values_list('pk', flat=True))), [1, 2, 3, 4, 5])
        self.assertEqual(sorted(list(ret[1].values_list('pk', flat=True))), range(1, 7))
        self.assertItemsEqual(ret[2], {1: [1, 2, 3, 4, 5, 6], 2: [], 3: [], 4: [], 5: []})

    def test_get_salescycles_by_last_activity_date_only_mentioned(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(self.crm_subscr_id,
                                                               user_id,
                                                               owned=False,
                                                               mentioned=True,
                                                               include_activities=True)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)), [4])
        self.assertEqual(list(ret[1].values_list('pk', flat=True)), [])
        self.assertItemsEqual(ret[2], {4: []})

    def test_get_salescycles_by_last_activity_date_only_followed(self):
        user_id = 1
        ret = SalesCycle.get_salescycles_by_last_activity_date(self.crm_subscr_id,
                                                               user_id,
                                                               owned=False,
                                                               mentioned=False,
                                                               followed=True,
                                                               include_activities=True)
        self.assertEqual(list(ret[0].values_list('pk', flat=True)), [3])


    def test_get_salescycles_by_last_activity_date_without_user_id(self):
        user_id = 10
        try:
            CRMUser.objects.get(pk=user_id)
        except CRMUser.DoesNotExist:
            raised = True
        else:
            raised = False
        finally:
            self.assertTrue(raised)

    def test_get_salescycles_by_contact(self):
        ret = SalesCycle.get_salescycles_by_contact(1)
        self.assertEqual(list(ret.values_list('pk', flat=True)), [1])

    def test_close_salescycle(self):
        self.assertNotEqual(self.sc1.status, 'C')
        products_with_values = {
            "1": 15000,
            "2": 13500
        }

        ret = self.sc1.close(products_with_values)
        self.assertIsInstance(ret[0], SalesCycle)
        self.assertIsInstance(ret[1], Activity)
        self.assertEqual(self.sc1.status, 'C')
        self.assertEqual(self.sc1.real_value.amount,
                         sum(products_with_values.values()))
        stat1 = SalesCycleProductStat.objects.get(sales_cycle=self.sc1,
                                                  product=Product.objects.get(id=1)).value
        stat2 = SalesCycleProductStat.objects.get(sales_cycle=self.sc1,
                                                  product=Product.objects.get(id=2)).value
        self.assertEqual(stat1, 15000)
        self.assertEqual(stat2, 13500)

    def test_set_result_by_amount(self):
        amount = 5000
        self.sc1.set_result_by_amount(amount)
        self.assertEqual(self.get_sc(pk=1).real_value.amount, amount)

    def test_delete_sales_cycle(self):
        sales_cycle = SalesCycle.objects.first()
        activities = sales_cycle.rel_activities.all()
        activities_count = activities.count()
        milestone = sales_cycle.milestone
        comments = sales_cycle.comments.all().count()
        product_stats = sales_cycle.product_stats.all()
        product_stats_count = product_stats.count()
        log_count = sales_cycle.log.all().count()
        act_comments = 0
        for activity in activities:
            act_comments += activity.comments.all().count()

        all_acts_count = Activity.objects.all().count()
        milestones_count = Milestone.objects.all().count()
        comments_count = Comment.objects.all().count()
        all_product_stats_count = SalesCycleProductStat.objects.all().count()
        products_count = Product.objects.all().count()
        all_log_count = SalesCycleLogEntry.objects.all().count()

        sales_cycle.delete()

        self.assertEqual(Activity.objects.all().count()+activities_count, all_acts_count)
        self.assertEqual(Comment.objects.all().count()+comments+act_comments, comments_count)
        self.assertEqual(SalesCycleLogEntry.objects.all().count()+log_count, all_log_count)

        self.assertEqual(SalesCycleProductStat.objects.all().count(), all_product_stats_count)
        self.assertEqual(Product.objects.all().count(), products_count)
        self.assertEqual(Milestone.objects.all().count(), milestones_count)

class ContactListTestCase(TestCase):
    fixtures = ['crmusers.json', 'contactlist.json', 'users.json', 'contacts.json']

    def setUp(self):
        super(self.__class__, self).setUp()
        self.contact_list = ContactList.objects.first()

    def test_create_contact_list(self):
        contact_list = ContactList(title = 'UNREGISTERED')
        self.assertEqual(contact_list.__unicode__(), 'UNREGISTERED')

    def test_add_contact(self):
        contact = Contact.objects.get(id=2)
        self.contact_list.add_contact(contact_id=contact.id)
        self.assertEqual(self.contact_list.contacts.get(id=2), contact)
        self.assertFalse(self.contact_list.add_contact(contact_id=1)[0])


    def test_contact_contact_lists(self):
        contact = Contact.objects.get(pk=1)
        self.assertEqual(self.contact_list,
                                contact.contact_list.get(id=1))


    def test_add_contacts(self):
        contact_1 = Contact.objects.get(id=1)
        contact_2 = Contact.objects.get(id=2)
        contact_3 = Contact.objects.get(id=3)
        contact_list = ContactList.objects.get(pk=2)
        self.assertEqual(contact_list.add_contacts(contact_ids=[contact_1.id, contact_2.id, contact_3.id]), [True, False, True])
        self.assertEqual(self.contact_list.contacts.get(id=contact_2.id), contact_2)
        self.assertEqual(self.contact_list.contacts.get(id=contact_3.id), contact_3)

    def test_check_contact(self):
        contact_1 = Contact.objects.get(id=1)
        contact_2 = Contact.objects.get(id=2)
        contact_3 = Contact.objects.get(id=3)
        self.contact_list.add_contact(contact_id=contact_2.id)
        self.assertTrue(self.contact_list.check_contact(contact_id=contact_1.id))
        self.assertTrue(self.contact_list.check_contact(contact_id=contact_2.id))
        self.assertTrue(self.contact_list.check_contact(contact_id=contact_3.id))

    def test_delete_contact(self):
        contact_1 = Contact.objects.get(id=1)
        contact_2 = Contact.objects.get(id=2)
        contact_3 = Contact.objects.get(id=3)
        contact_list2 = ContactList(title='Test Contact list')
        contact_list2.save()
        contact_list2.add_contacts(contact_ids=[contact_1.id, contact_2.id])
        self.assertFalse(contact_list2.delete_contact(contact_id=contact_3.id))
        self.assertTrue(contact_list2.delete_contact(contact_id=contact_2.id))
        self.assertFalse(contact_list2.delete_contact(contact_id=contact_2.id))
        self.assertTrue(contact_list2.delete_contact(contact_id=contact_1.id))
        self.assertFalse(contact_list2.delete_contact(contact_id=contact_1.id))
        self.assertEqual(contact_list2.count(), 0)

    def test_count(self):
        contact_1 = Contact.objects.get(id=1)
        contact_2 = Contact.objects.get(id=2)
        contact_3 = Contact.objects.get(id=3)
        contact_list2 = ContactList(title='Test Contact list')
        contact_list2.save()
        contact_list2.add_contacts(contact_ids=[contact_1.id, contact_2.id, contact_3.id])
        self.assertEqual(contact_list2.count(), 3)

class FilterTestCase(TestCase):
    fixtures = ['filters.json', 'crmusers.json', 'users.json']

    def setUp(self):
        super(self.__class__, self).setUp()
        self.filter = Filter.objects.first()

    def test_create_filter(self):
        crmuser = CRMUser.objects.first()
        new_filter = Filter(title='New filter', filter_text='Test Filter', owner=crmuser)
        self.assertEqual(new_filter.title, 'New filter')
        self.assertEqual(new_filter.base, 'all')

    def test_delete_filter(self):
        count_before = Filter.objects.all().count()
        filter_last = Filter.objects.last()
        filter_last.delete()
        count_after = Filter.objects.all().count()
        self.assertEqual(count_before-1, count_after)

    def test_create_filter_with_base(self):
        crmuser = CRMUser.objects.first()
        new_filter = Filter(title='New filter', filter_text='Test Filter', owner=crmuser, base='cold')
        self.assertEqual(new_filter.title, 'New filter')
        self.assertEqual(new_filter.base, 'cold')
        self.assertEqual(new_filter.owner, crmuser)


class MilestoneTestCase(TestCase):
    fixtures = ['subscriptions.json', 'services.json', 'companies.json', 'users.json']

    def setUp(self):
        super(self.__class__, self).setUp()
        self.milestone = Milestone.objects.first()

    def test_create_default_subscription(self):
        before = Milestone.objects.all().count()
        s = Subscription(service=Service.objects.first(), organization = Company.objects.last(), user=User.objects.last())
        s.save()
        after = Milestone.objects.all().count()
        actual = after
        expected = before+7
        expected_titles = ['Звонок/Заявка',
                            'Отправка КП',
                            'Согласование договора',
                            'Выставление счета',
                            'Контроль оплаты',
                            'Предоставление услуги',
                            'Upsales']
        expected_colors = ['#F4B59C',
                            '#F59CC8',
                            '#A39CF4',
                            '#9CE5F4',
                            '#9CF4A7',
                            '#D4F49B',
                            '#F4DC9C'
                            ]
        self.assertEqual(actual, expected)
        for milestone in Milestone.objects.filter(subscription_id = s.pk):
            self.assertTrue(milestone.title.encode('utf-8') in expected_titles)
            self.assertTrue(milestone.color_code in expected_colors)
            self.assertEqual(expected_titles.index(milestone.title.encode('utf-8')), expected_colors.index(milestone.color_code))


class ResourceTestMixin(object):
    fixtures = ['companies.json', 'services.json', 'users.json',
                'subscriptions.json', 'comments.json',
                'crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'products.json',
                'mentions.json', 'values.json', 'emails.json', 'contactlist.json', 'share.json',
                'feedbacks.json', 'salescycle_product_stat.json', 'filters.json', 'milestones.json',
                'sc_log_entry.json']

    def get_user(self):
        from alm_user.models import User
        self.user = User.objects.get(pk=1)
        self.user_password = '123'

    def get_credentials(self):
        self.get_user()
        self.api_client.client.login(username=self.user.email, password=self.user_password)
        return self.create_basic(self.user.email, self.user_password)


class SalesCycleResourceTest(ResourceTestMixin, ResourceTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()
        self.get_credentials()
        self.api_path_sales_cycle = '/api/v1/sales_cycle/'

        self.get_resp = lambda path: self.api_client.get(
            self.api_path_sales_cycle + path,
            format='json',
            HTTP_HOST='localhost')
        self.get_des_res = lambda path: self.deserialize(self.get_resp(path))
        self.sales_cycle = SalesCycle.objects.first()

        self.QUERYSET_OPEN_CYCLES = SalesCycle.objects.filter(subscription_id=1, is_global=False, status__in=[SalesCycle.NEW, SalesCycle.PENDING])

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_resp(''))

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_des_res('')['meta']['total_count'] > 0)

    def test_get_detail_json(self):
        self.assertEqual(
            self.get_des_res(str(self.sales_cycle.pk)+'/')['title'],
            self.sales_cycle.title
            )
        self.assertEqual(
            self.get_des_res(str(self.sales_cycle.pk)+'/')['id'],
            self.sales_cycle.id
            )

    def test_create_sales_cycle(self):
        post_data = {
            'title': 'new SalesCycle from test_unit',
            'contact_id': Contact.objects.last().pk
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

    def test_create_sales_cycle_with_empty_title(self):
        post_data = {
            'title': '',
            'contact_id': Contact.objects.last().pk
        }

        count = SalesCycle.objects.count()
        raised = False
        try:
            resp = self.api_client.post(
                self.api_path_sales_cycle, format='json', data=post_data)
        except Exception:
            raised= True

        self.assertTrue(raised)


    @skipIf(True, "Resource needs in overwrite save_m2m() to create with M2M-relations")
    def test_patch_sales_cycle_with_products(self):
        patch_data = {
            'product_ids': [1, 2, 3]
        }
        before = self.sales_cycle.products.count()

        resp = self.api_client.patch(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/',
            format='json',
            data=patch_data)
        self.assertHttpAccepted(resp)
        self.assertNotEqual(before, self.sales_cycle.products.count())

    def test_get_product_ids(self):
        resp = self.api_client.get(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/products/',
            format='json')
        resp = self.deserialize(resp)
        self.assertTrue('object_ids' in resp)
        self.assertIsInstance(resp['object_ids'], list)
        self.assertEqual(len(resp['object_ids']), self.sales_cycle.products.count())

    def test_update_product_ids(self):
        put_data = {
            'object_ids': [1, 2, 3]
        }
        before = self.sales_cycle.products.count()
        resp = self.api_client.put(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/products/',
            format='json', data=put_data)
        self.assertHttpAccepted(resp)
        self.assertNotEqual(before, self.sales_cycle.products.count())
        resp = self.deserialize(resp)
        self.assertEqual(len(resp['object_ids']), self.sales_cycle.products.count())

    @skipIf(True, "now, activities is not presented in SalesCycleResource")
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
        # print self.api_client.post(
        #     self.api_path_sales_cycle, format='json', data=post_data)

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

    def test_close_sales_cycle(self):
        self.sales_cycle.is_global = False
        self.sales_cycle.save()
        self.assertNotEqual(self.sales_cycle.status, 'C')
        put_data = {
            "1": 15000,
            "2": 13500
        }
        resp = self.api_client.put(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/close/',
            format='json', data=put_data)
        self.assertHttpAccepted(resp)
        resp = self.deserialize(resp)
        self.assertTrue('activity' in resp)
        self.assertTrue('sales_cycle' in resp)

        self.assertEqual(resp['sales_cycle']['status'], 'C')
        self.assertEqual(resp['sales_cycle']['real_value']['value'],
                         sum(put_data.values()))
        self.assertEqual(resp['activity']['feedback_status'], Feedback.OUTCOME)
        stat1 = SalesCycleProductStat.objects.get(sales_cycle=self.sales_cycle,
                                                  product=Product.objects.get(id=1)).value
        stat2 = SalesCycleProductStat.objects.get(sales_cycle=self.sales_cycle,
                                                  product=Product.objects.get(id=2)).value
        self.assertEqual(stat1, 15000)
        self.assertEqual(stat2, 13500)
        self.sales_cycle.is_global = True
        self.sales_cycle.save()

    def test_closeGlobalCycleRaiseError(self):
        owner = CRMUser.objects.first()
        sales_cycle = SalesCycle.objects.get(owner=owner, is_global=True, contact_id=1)
        put_data = {
            '1': 10000,
            '2': 3000
        }
        resp = self.api_client.put(
            self.api_path_sales_cycle + str(sales_cycle.pk) + '/close/',
            format='json', data=put_data)
        self.assertHttpUnauthorized(resp)

    def test_delete_cycle_service(self):
        sales_cycle = SalesCycle.objects.get(pk=2)
        activities = sales_cycle.rel_activities.all()
        activities_count = activities.count()
        milestone = sales_cycle.milestone
        comments = sales_cycle.comments.all().count()
        product_stats = sales_cycle.product_stats.all()
        product_stats_count = product_stats.count()
        log_count = sales_cycle.log.all().count()
        act_comments = 0
        for activity in activities:
            act_comments += activity.comments.all().count()

        all_acts_count = Activity.objects.all().count()
        milestones_count = Milestone.objects.all().count()
        comments_count = Comment.objects.all().count()
        all_product_stats_count = SalesCycleProductStat.objects.all().count()
        products_count = Product.objects.all().count()
        all_log_count = SalesCycleLogEntry.objects.all().count()

        sales_cycle_pk = sales_cycle.pk
        acts_pks = list(sales_cycle.rel_activities.all().values_list('id', flat=True))

        resp = self.api_client.get(
            self.api_path_sales_cycle+str(sales_cycle.pk)+'/delete/')
        self.assertHttpAccepted(resp)

        self.assertEqual(self.deserialize(resp)['objects']['activities'], acts_pks)
        self.assertEqual(self.deserialize(resp)['objects']['sales_cycle'], sales_cycle_pk)

        self.assertEqual(Activity.objects.all().count()+activities_count, all_acts_count)
        self.assertEqual(Comment.objects.all().count()+comments+act_comments, comments_count)
        self.assertEqual(SalesCycleLogEntry.objects.all().count()+log_count, all_log_count)

        self.assertEqual(SalesCycleProductStat.objects.all().count(), all_product_stats_count)
        self.assertEqual(Product.objects.all().count(), products_count)
        self.assertEqual(Milestone.objects.all().count(), milestones_count)

    def test_try_delete_global(self):
        sales_cycle = SalesCycle.objects.first()
        activities = sales_cycle.rel_activities.all()
        activities_count = activities.count()
        milestone = sales_cycle.milestone
        comments = sales_cycle.comments.all().count()
        product_stats = sales_cycle.product_stats.all()
        product_stats_count = product_stats.count()
        log_count = sales_cycle.log.all().count()
        act_comments = 0
        for activity in activities:
            act_comments += activity.comments.all().count()

        all_acts_count = Activity.objects.all().count()
        milestones_count = Milestone.objects.all().count()
        comments_count = Comment.objects.all().count()
        all_product_stats_count = SalesCycleProductStat.objects.all().count()
        products_count = Product.objects.all().count()
        all_log_count = SalesCycleLogEntry.objects.all().count()

        resp = self.api_client.get(
            self.api_path_sales_cycle+str(sales_cycle.pk)+'/delete/')

        self.assertHttpBadRequest(resp)

        self.assertEqual(Activity.objects.all().count(), all_acts_count)
        self.assertEqual(Comment.objects.all().count(), comments_count)
        self.assertEqual(SalesCycleLogEntry.objects.all().count(), all_log_count)
        self.assertEqual(SalesCycleProductStat.objects.all().count(), all_product_stats_count)
        self.assertEqual(Product.objects.all().count(), products_count)
        self.assertEqual(Milestone.objects.all().count(), milestones_count)
        
    def test_limit_for_mobile(self):
        resp = self.api_client.get(self.api_path_sales_cycle + '?limit_for=mobile')
        des_resp = self.deserialize(resp)

        self.assertEqual(len(des_resp['objects']), self.QUERYSET_OPEN_CYCLES.count())


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

        self.QUERYSET_ACTIVITIES_FOR_MOBILE = Activity.objects.filter(
                subscription_id=1
            ).filter(Activity.get_filter_for_mobile())

    def test_get_list_valid_json(self):        
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        resp_activity = self.get_detail_des(self.activity.pk)

        self.assertEqual(resp_activity['description'], self.activity.description)
        self.assertEqual(resp_activity['author_id'], self.activity.owner.id)
        self.assertEqual(resp_activity['feedback_status'], self.activity.feedback.status)
        self.assertTrue('has_read' in resp_activity)

    def test_spray_activity(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': 'new activity',
            'sales_cycle_id': sales_cycle.id,
            'feedback_status': Feedback.OUTCOME
        }
        unfollowers = [
            unfollow.id for unfollow in sales_cycle.contact.unfollowers.all()]
        universe = CRMUser.objects.all().values_list('id', flat=True)

        expected_objects = len(set(universe) - set(unfollowers))
        self.api_client.post(self.api_path_activity,
                             format='json', data=post_data)
        actual_objects = Activity.objects.last().recipients.count()
        self.assertEqual(actual_objects, expected_objects)

    def test_spray_activityWithUnfollower(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': 'new activity',
            'sales_cycle_id': sales_cycle.id,
            'feedback_status': Feedback.OUTCOME
        }
        unfollowers = [
            unfollow.id for unfollow in sales_cycle.contact.unfollowers.all()]
        universe = CRMUser.objects.all().values_list('id', flat=True)
        for user_id in universe:
            if not user_id in unfollowers:
                user = CRMUser.objects.get(pk=user_id)
                user.unfollow_list.add(sales_cycle.contact)
                break
        expected_objects = len(set(universe) - set(unfollowers))
        # if no more user
        if expected_objects:
            expected_objects -= 1
        self.api_client.post(self.api_path_activity,
                             format='json', data=post_data)
        actual_objects = Activity.objects.last().recipients.count()
        self.assertEqual(actual_objects, expected_objects)

    def test_markZeroActivitiesAsRead(self):
        import json
        post_data = []
        response = self.api_client.post(
            self.api_path_activity + 'read/', format='json', data=post_data)
        response = json.loads(response.content)
        self.assertEqual(response['success'], 0)

    def test_markOneActivityAsRead(self):
        import json
        self.test_spray_activity()
        act = Activity.objects.last()

        expected = act.recipients.count() - 1
        post_data = [act.pk]
        response = self.api_client.post(
            self.api_path_activity + 'read/', format='json', data=post_data)
        response = json.loads(response.content)
        act = Activity.objects.last()
        actual = act.recipients.filter(has_read=False).count()
        self.assertEqual(response['success'], 1)
        self.assertEqual(expected, actual)

    def test_markTwoActivitiesAsRead(self):
        import json
        expected, actual = [], []
        self.test_spray_activity()
        self.test_spray_activity()
        acts = list(Activity.objects.all())[-2:]
        for act in acts:
            expected.append(act.recipients.count() - 1)
        post_data = map(lambda act: act.pk, acts)
        response = self.api_client.post(
            self.api_path_activity + 'read/', format='json', data=post_data)
        response = json.loads(response.content)

        acts = list(Activity.objects.all())[-2:]
        for act in acts:
            actual.append(act.recipients.filter(has_read=False).count())

        self.assertEqual(response['success'], 2)
        for _act, _exp in zip(actual, expected):
            self.assertEqual(_act, _exp)

    def test_create_activity_with_feedback(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': 'new activity, test_unit',
            'sales_cycle_id': sales_cycle.id,
            'feedback_status': "$"
        }
        count = Activity.objects.all().count()
        count2 = sales_cycle.rel_activities.count()
        resp = self.api_client.post(self.api_path_activity, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(Activity.objects.all().count(), count + 1)
        # verify that new one has been added.
        self.assertEqual(sales_cycle.rel_activities.count(), count2 + 1)
        activity = sales_cycle.rel_activities.last()
        # verify that subscription_id was set
        self.assertIsInstance(activity.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(activity.owner, CRMUser)
        self.assertIsInstance(activity.feedback, Feedback)
        self.assertEqual(Activity.objects.last().feedback,
                         Feedback.objects.last())


    def test_create_activity_with_mentions_and_hashtags(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': '#almacloud @[1:Bruce Wayne] has sold #almacrm to @[2:Nurlan Abiken]',
            'sales_cycle_id': sales_cycle.id,
            'feedback_status': "$"
        }
        count = Activity.objects.all().count()
        count2 = sales_cycle.rel_activities.count()
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        resp = self.api_client.post(self.api_path_activity, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(Activity.objects.all().count(), count + 1)
        # verify that new one has been added.
        self.assertEqual(sales_cycle.rel_activities.count(), count2 + 1)
        activity = sales_cycle.rel_activities.last()
        # verify that subscription_id was set
        self.assertIsInstance(activity.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(activity.owner, CRMUser)
        self.assertIsInstance(activity.feedback, Feedback)
        self.assertEqual(Activity.objects.last().feedback,
                         Feedback.objects.last())
        self.assertEqual(hashtag_count+2, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+2, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+2, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))


    def test_create_activity_without_feedback(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': 'new activity, test_unit',
            'sales_cycle_id': sales_cycle.id
        }
        count = Activity.objects.all().count()
        count2 = sales_cycle.rel_activities.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_activity, format='json', data=post_data))
        self.assertEqual(Activity.objects.all().count(), count+1)
        # verify that new one has been added.
        self.assertEqual(sales_cycle.rel_activities.count(), count2 + 1)
        activity = sales_cycle.rel_activities.last()
        # verify that subscription_id was set
        self.assertIsInstance(activity.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(activity.owner, CRMUser)

    def test_delete_activity(self):
        count = Activity.objects.count()
        activity = Activity.objects.get(id=2)
        self.assertHttpAccepted(
            self.api_client.delete(self.api_path_activity + '%s/' % activity.pk, format='json'))
        # verify that one sales_cycle has been deleted.
        self.assertEqual(Activity.objects.count(), count - 1)

    def test_update_activity_via_put(self):
        # get exist product data
        activity = Activity.objects.last()
        activity_data = self.get_detail_des(activity.pk)
        sales_cycle_id = SalesCycle.objects.last().id
        new_feedback = "5"
        # update it
        t = '_UPDATED!'
        activity_data['description'] += t
        activity_data['feedback_status'] = new_feedback
        activity_data['sales_cycle_id'] = sales_cycle_id
        # PUT it
        self.api_client.put(self.api_path_activity + '%s/' % (activity.pk),
                            format='json', data=activity_data)
        # check
        activity_last = Activity.objects.last()
        self.assertEqual(activity_last.description, activity.description + t)
        self.assertEqual(self.get_detail_des(activity.pk)['description'], activity.description + t)

        self.assertEqual(activity_last.feedback.status, new_feedback)
        self.assertEqual(self.get_detail_des(activity.pk)['feedback_status'], new_feedback)

        activity_last = Activity.objects.last()
        self.assertEqual(self.get_detail_des(activity.pk)['sales_cycle_id'], sales_cycle_id)
        self.assertEqual(sales_cycle_id, activity_last.sales_cycle.id)


    def test_update_activity_via_put_with_hashtag_and_mention(self):
        # get exist product data
        activity = Activity.objects.last()
        activity_data = self.get_detail_des(activity.pk)
        sales_cycle_id = SalesCycle.objects.last().id
        new_feedback = "5"
        # update it
        t = '_UPDATED! #updated by @[1:Bruce Wayne]'
        activity_data['description'] += t
        activity_data['feedback_status'] = new_feedback
        activity_data['sales_cycle_id'] = sales_cycle_id
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()

        # PUT it
        self.api_client.put(self.api_path_activity + '%s/' % (activity.pk),
                            format='json', data=activity_data)
        # check
        activity_last = Activity.objects.last()
        self.assertEqual(activity_last.description, activity.description + t)
        self.assertEqual(self.get_detail_des(activity.pk)['description'], activity.description + t)

        self.assertEqual(activity_last.feedback.status, new_feedback)
        self.assertEqual(self.get_detail_des(activity.pk)['feedback_status'], new_feedback)

        activity_last = Activity.objects.last()
        self.assertEqual(self.get_detail_des(activity.pk)['sales_cycle_id'], sales_cycle_id)
        self.assertEqual(sales_cycle_id, activity_last.sales_cycle.id)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   

    def test_move(self):
        activity = Activity.objects.first()
        prev_sales_cycle = activity.sales_cycle
        next_sales_cycle = SalesCycle.objects.last()
        prev_acts_count = prev_sales_cycle.rel_activities.all().count()
        next_acts_count = next_sales_cycle.rel_activities.all().count()
        post_data={
            'sales_cycle_id': next_sales_cycle.pk
            }
        resp =  self.api_client.post(self.api_path_activity + '%s/move/' % activity.pk, 
                                    format='json', data=post_data)
        self.assertHttpAccepted(resp)
        self.assertEqual(Activity.objects.first().sales_cycle, next_sales_cycle)
        self.assertEqual(self.deserialize(resp)['objects']['activity']['id'], activity.id)
        self.assertEqual(self.deserialize(resp)['objects']['prev_sales_cycle']['id'], prev_sales_cycle.id)
        self.assertEqual(self.deserialize(resp)['objects']['next_sales_cycle']['id'], next_sales_cycle.id)
        self.assertEqual(list(self.deserialize(resp)['objects']['prev_sales_cycle']['activities']), 
                        list(prev_sales_cycle.rel_activities.all().values_list('id', flat=True)))
        self.assertEqual(list(self.deserialize(resp)['objects']['next_sales_cycle']['activities']), 
                        list(next_sales_cycle.rel_activities.all().values_list('id', flat=True)))
        self.assertEqual(prev_sales_cycle.rel_activities.all().count()+1, prev_acts_count)

        # resp =  self.api_client.post(self.api_path_activity + '%s/move/' % activity.pk)
        # self.assertHttpBadRequest(resp)

    def test_limit_for_mobile(self):
        resp = self.api_client.get(self.api_path_activity + '?limit_for=mobile')
        des_resp = self.deserialize(resp)
        self.assertEqual(len(des_resp['objects']), self.QUERYSET_ACTIVITIES_FOR_MOBILE.count())


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
        }

        count = sales_cycle.products.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_product, format='json', data=post_data))
        product = Product.objects.last()
        self.assertEqual(product.name, 'new product')
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

    def test_replace_products(self):
        post_data = {
            "sales_cycle_ids": [1, 2, 3]
        }
        before = self.product.sales_cycles.count()
        resp = self.api_client.post(
            self.api_path_product+str(self.product.pk)+'/replace_cycles/',
            format='json', data=post_data)
        self.assertHttpAccepted(resp)
        self.assertNotEqual(before, self.product.sales_cycles.count())


class ContactResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_contact = '/api/v1/contact/'
        self.api_path_contact_products_f = '/api/v1/contact/%s/products/'
        self.api_path_contact_activities_f = '/api/v1/contact/%s/activities/'
        self.api_path_import = '/api/v1/contact/import/'


        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_contact,
                                                 format='json',
                                                 HTTP_HOST='localhost')

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

         #get list for recent contacts
        self.get_list_import_resp = self.api_client.get(self.api_path_contact+'import/',
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        self.get_list_import_des = self.deserialize(self.get_list_import_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_contact+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')

        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.contact = Contact.objects.first()
        self.crm_subscr_id = 1

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)
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
            'vcard': {"fn": "Nurlan Abiken"},
            'note': 'some text'
        }
        count = Contact.objects.count()
        resp = self.api_client.post(
            self.api_path_contact, format='json', data=post_data)
        self.assertHttpOK(resp)
        # verify that new one has been added.
        self.assertEqual(Contact.objects.count(), count + 1)
        created_contact = Contact.objects.last()
        self.assertEqual(created_contact.sales_cycles.first().title, GLOBAL_CYCLE_TITLE.decode('utf-8'))
        # print resp

    def test_delete_contact(self):
        count = Contact.objects.count()

        count_related_sales_cycles = self.contact.sales_cycles.all().count()
        count_all_sales_cycle = SalesCycle.objects.all().count()

        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_contact + '%s/' % self.contact.pk, format='json'))
        count_sales_cycle = SalesCycle.objects.all().count()
        # verify that one contact been deleted.
        self.assertEqual(Contact.objects.count(), count - 1)
        self.assertEqual(count_sales_cycle, count_all_sales_cycle - count_related_sales_cycles)

    def test_get_last_contacted(self):
        user = CRMUser.objects.first()
        recent = Contact.get_contacts_by_last_activity_date(subscription_id = user.subscription_id, 
                                                            user_id = user.id)
        self.assertEqual(len(self.get_list_recent_des['objects']),
                         len(recent))

    def test_get_cold_base(self):
        cold_base = Contact.get_cold_base(self.crm_subscr_id)
        self.assertEqual(
            len(self.get_list_cold_base_des['objects']),
            len(cold_base)
            )

    def test_get_leads(self):
        leads = Contact.get_contacts_by_status(self.crm_subscr_id, Contact.LEAD)
        self.assertEqual(len(self.get_list_leads_des['objects']),
                         len(leads))

    def test_share_contact(self):
        count = Share.objects.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'share_contact/?contact_id=1&share_from=1&share_to=2'))

        self.assertEqual(Share.objects.count(), count+1)

        share_to = Share.objects.last().share_to
        share_from = Share.objects.last().share_from

        self.assertEqual(share_from, CRMUser.objects.get(pk=1))
        self.assertEqual(share_to, CRMUser.objects.get(pk=2))

    def test_share_contacts(self):
        count = Share.objects.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'share_contacts/?contact_ids=%5B2%2C3%2C4%5D&share_from=1&share_to=2'))

        self.assertEqual(Share.objects.count(), count+3)

        share_to = CRMUser.objects.get(id=Share.objects.last().share_to.id)
        share_from = CRMUser.objects.get(id=Share.objects.last().share_from.id)

        self.assertEqual(share_from, CRMUser.objects.get(pk=1))
        self.assertEqual(share_to, CRMUser.objects.get(pk=2))

    def test_search(self):
        search_text_A = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                         search_text='A',
                                                         search_params=[('fn', 'startswith')],
                                                         order_by=[])
        srch_tx_A_ord_dc = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                            search_text='A',
                                                            search_params=[('fn', 'startswith')],
                                                            order_by=['fn', 'desc'])
        srch_by_bday = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                        search_text='1991-09-10',
                                                        search_params=['bday'],
                                                        order_by=[])
        srch_by_email = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                         search_text='mus',
                                                         search_params=[('email__value', 'startswith')],
                                                         order_by=[])


        get_list_search_resp = self.api_client.get(self.api_path_contact+
                                            "search/?search_params=%5B('fn'%2C+'startswith')%5D&search_text=A",
                                            format='json',
                                            HTTP_HOST='localhost')

        get_list_search_ord_dc_resp = self.api_client.get(self.api_path_contact+
                                            "search/?search_params=%5B('fn'%2C+'startswith')%5D&order_by=%5B'fn'%2C'desc'%5D&search_text=A",
                                            format='json',
                                            HTTP_HOST='localhost')

        get_list_search_by_bday_resp = self.api_client.get(self.api_path_contact+
                                            "search/?search_params=%5B'bday'%5D&search_text=1991-09-10",
                                            format='json',
                                            HTTP_HOST='localhost')

        get_list_search_by_email_resp = self.api_client.get(self.api_path_contact+
                                            "search/?search_params=%5B('email__value'%2C+'startswith')%5D&search_text=mus",
                                            format='json',
                                            HTTP_HOST='localhost')

        get_list_search_des = self.deserialize(get_list_search_resp)
        get_list_search_ord_dc_des = self.deserialize(get_list_search_ord_dc_resp)
        get_list_search_by_bday_des = self.deserialize(get_list_search_by_bday_resp)
        get_list_search_by_email_resp = self.deserialize(get_list_search_by_email_resp)

        self.assertEqual(get_list_search_des['objects'][0]['vcard']['fn'], search_text_A[0].vcard.fn)
        self.assertEqual(get_list_search_des['objects'][1]['vcard']['fn'], search_text_A[1].vcard.fn)

        self.assertEqual(get_list_search_des['objects'][0]['vcard']['fn'], srch_tx_A_ord_dc[1].vcard.fn)
        self.assertEqual(get_list_search_des['objects'][1]['vcard']['fn'], srch_tx_A_ord_dc[0].vcard.fn)

        self.assertEqual(get_list_search_ord_dc_des['objects'][0]['vcard']['fn'], srch_tx_A_ord_dc[0].vcard.fn)
        self.assertEqual(get_list_search_ord_dc_des['objects'][1]['vcard']['fn'], srch_tx_A_ord_dc[1].vcard.fn)
        self.assertEqual(get_list_search_by_bday_des['objects'][0]['vcard']['fn'], srch_by_bday[0].vcard.fn)

        self.assertEqual(get_list_search_by_email_resp['objects'][0]['vcard']['fn'], srch_by_email[0].vcard.fn)
        self.assertEqual(get_list_search_by_email_resp['objects'][1]['vcard']['fn'], srch_by_email[1].vcard.fn)

    def test_get_products(self):
        resp = self.api_client.get(
            self.api_path_contact_products_f % (self.contact.pk),
            format='json',
            HTTP_HOST='localhost'
            )
        self.assertEqual(len(self.deserialize(resp)['objects']),
                         len(Contact.get_contact_products(self.contact.pk)))

    def test_get_activities(self):
        resp = self.api_client.get(
            self.api_path_contact_activities_f % (self.contact.pk),
            format='json',
            HTTP_HOST='localhost'
            )
        self.assertEqual(len(self.deserialize(resp)['objects']),
                         len(Contact.get_contact_activities(self.contact.pk)))

    def test_import_from_xls(self):          
        count = Contact.objects.all().count()
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/contacts.xls')
        import base64
        post_data={
            'filename': 'aliya.xlsx',
            'uploaded_file': base64.b64encode(open(file_path, "rb").read())
            }

        resp = self.api_client.post(
            self.api_path_contact+"import/", format='json', data=post_data)
        self.assertContains(resp, '"error":', status_code=400)
        self.assertEqual(Contact.objects.all().count(), count)
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/correct_contacts_format.xlsx')
        post_data={
            'filename': 'aliya.xlsx',
            'uploaded_file': base64.b64encode(open(file_path, "rb").read())
            }
        resp = self.api_client.post(
            self.api_path_contact+"import/", format='json', data=post_data)
        self.assertHttpOK(resp)

        self.assertEqual(Contact.objects.all().count(), count+17)
        des_resp = self.deserialize(resp)
        self.assertTrue('contact_list' in des_resp)
        self.assertEqual(des_resp['contact_list']['title'], 'aliya.xlsx')

    def test_import_from_vcard(self):
        uploaded_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/nurlan.vcf')
        import base64
        post_data = {
            'filename': 'nurlan.vcf',
            "uploaded_file": base64.b64encode(open(uploaded_file, "r").read())
        }

        amount_before_import = SalesCycle.objects.all().count()
        amout_of_contacts_before_import = Contact.objects.all().count()

        resp = self.api_client.post(
            self.api_path_import, format='json', data=post_data)

        self.assertHttpOK(resp)


        amount_after_import = SalesCycle.objects.all().count()

        contact1 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Aslan',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        contact2 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Serik',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        contact3 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Almat',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        contact4 = Contact.filter_contacts_by_vcard(self.crm_subscr_id,
                                                    search_text='Mukatayev',
                                                    search_params=[('fn', 'icontains')],
                                                    order_by=[])
        self.assertEqual(amount_after_import, amount_before_import+3)
        self.assertTrue(c.sales_cycles.first().title == GLOBAL_CYCLE_TITLE for c in contact4)
        # self.assertTrue('global_sales_cycle' in self.deserialize(resp)['success'][i].keys()
        #                 for i in range(0,3))
        # self.assertEqual(self.deserialize(resp)['success'][0]['global_sales_cycle']['id'],
        #                 contact1.first().sales_cycles.get(is_global=True).id)
        # self.assertEqual(self.deserialize(resp)['success'][1]['global_sales_cycle']['id'],
        #                 contact2.first().sales_cycles.get(is_global=True).id)
        # self.assertEqual(self.deserialize(resp)['success'][2]['global_sales_cycle']['id'],
        #                 contact3.first().sales_cycles.get(is_global=True).id)
        self.assertEqual(len(Contact.objects.all()), amout_of_contacts_before_import+3)
        self.assertEqual(len(contact4), 3)
        self.assertTrue(contact1.first() in Contact.objects.all())
        self.assertTrue(contact2.first() in Contact.objects.all())
        self.assertTrue(contact3.first() in Contact.objects.all())
        des_resp = self.deserialize(resp)
        self.assertTrue('contact_list' in des_resp)
        self.assertEqual(des_resp['contact_list']['title'], 'nurlan.vcf')


class ContactListResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_contact_list = '/api/v1/contact_list/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_contact_list,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_contact_list+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.contact_list = ContactList.objects.first()


    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.contact_list.pk)['title'],
            self.contact_list.title
            )

    def test_create_contact_list(self):
        contact = Contact.objects.last()
        post_data = {
            'owner': Contact.objects.first(),
            'title': 'Mobiliuz',
            'contacts': [contact.pk]
        }

        count = contact.contact_list.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_contact_list, format='json', data=post_data))
        contact_list = contact.contact_list.last()
        # verify that new one has been added.
        self.assertEqual(contact.contact_list.count(), count + 1)
        self.assertEqual(ContactList.objects.last().title, 'Mobiliuz')

    def test_delete_contact_list(self):
        count = ContactList.objects.count()
        contact_list = ContactList.objects.last()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_contact_list + '%s/' % contact_list.pk, format='json'))
        # verify that one sales_cycle has been deleted.
        self.assertEqual(ContactList.objects.count(), count - 1)
        count = count - 1
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_contact_list + '%s/' % self.contact_list.pk, format='json'))
        self.assertEqual(ContactList.objects.count(), count - 1)


    def test_delete_user_from_contact_list(self):
        api_path_delete_contact = self.api_path_contact_list+'%s/delete_contact/' % self.contact_list.pk
        contact_id = self.contact_list.contacts.first().id
        count = self.contact_list.contacts.all().count()
        self.assertHttpOK(self.api_client.get(api_path_delete_contact+'?contact_id=%d'%contact_id))
        self.assertEqual(self.contact_list.contacts.all().count(), count-1)
        self.assertHttpOK(self.api_client.get(api_path_delete_contact+'?contact_id=%d'%contact_id))
        self.assertEqual(self.contact_list.contacts.all().count(), count-1)

    def test_add_contacts(self):
        contact = Contact.objects.get(pk=3)
        contact3 = Contact.objects.get(pk=2)
        contact4 = Contact.objects.get(pk=1)
        contacts = [contact.pk, contact3.pk, contact4.pk]
        contact_list = ContactList.objects.get(pk=2)

        api_path_add_contact = self.api_path_contact_list+'%s/add_contacts/' % contact_list.pk
        count = contact_list.contacts.all().count()

        self.assertHttpOK(self.api_client.get(api_path_add_contact+'?contact_ids=%s'%[contact.pk]))
        self.assertEqual(contact_list.contacts.all().count(), count+1)

        self.assertHttpOK(self.api_client.get(api_path_add_contact+'?contact_ids=%s'%[contact3.pk]))
        self.assertEqual(contact_list.contacts.all().count(), count+1)

        count = count+1
        self.assertHttpOK(self.api_client.get(api_path_add_contact+'?contact_ids=%s'%contacts))
        self.assertEqual(contact_list.contacts.all().count(), count+1)

        contact_list2 = ContactList(title='HP Webcam')
        contact_list2.save()
        count = contact_list2.contacts.all().count()
        api_path_add_contact = self.api_path_contact_list+'%s/add_contacts/' % contact_list2.pk

        self.assertHttpOK(self.api_client.post(api_path_add_contact+'?contact_ids=%s'%contacts))
        self.assertEqual(contact_list2.contacts.all().count(), count+3)

    def test_check_contact(self):
        contact = Contact.objects.get(pk=1)
        contact2 = Contact.objects.get(pk=2)

        api_path_check_contact = self.api_path_contact_list+'%s/check_contact/?contact_id=%s' % \
                                                            (self.contact_list.pk, contact.pk)

        get_list_check_contact_resp = self.api_client.get(api_path_check_contact,
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        get_list_check_contact_des = self.deserialize(get_list_check_contact_resp)
        self.assertTrue(get_list_check_contact_des['success'])

        api_path_check_contact = self.api_path_contact_list+'%s/check_contact/?contact_id=%s' % \
                                                            (self.contact_list.pk, 4)

        get_list_check_contact_resp = self.api_client.get(api_path_check_contact,
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        get_list_check_contact_des = self.deserialize(get_list_check_contact_resp)
        self.assertFalse(get_list_check_contact_des['success'])

    def test_get_contacts(self):
        contact = Contact.objects.get(pk=1)

        api_path_get_contact = self.api_path_contact_list+'%s/contacts/' % \
                                                            self.contact_list.pk

        get_list_get_contact_resp = self.api_client.get(api_path_get_contact,
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        get_list_get_contact_des = self.deserialize(get_list_get_contact_resp)

        contacts = self.contact_list.contacts.all()
        self.assertEqual(get_list_get_contact_des['objects'][0]['id'], contacts.first().id)


    def test_update_contactlist_via_put(self):
        # get exist product data
        p = ContactList.objects.first()
        contactlist = self.get_detail_des(p.pk)
        # update it
        contactlist['contacts'] = [1]
        # PUT it
        self.api_client.put(self.api_path_contact_list + '%s/' % (p.pk),
                            format='json', data=contactlist)
        # check
        self.assertEqual(self.get_detail_des(p.pk)['contacts'], [1])


class AppStateResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_app_state_list = '/api/v1/app_state/'


        self.get_detail_resp = \
            lambda pk: self.api_client.get(
                self.api_path_app_state_list+str(pk)+'/',
                format='json',
                HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.subscription = Subscription.objects.first()

    def test_get(self):
        app_state = self.get_detail_des(self.subscription.service.slug)
        self.assertHttpOK(self.get_detail_resp(self.subscription.service.slug))
        self.assertTrue('objects' in app_state)
        self.assertTrue('users' in app_state['objects'])
        self.assertTrue('company' in app_state['objects'])
        self.assertTrue('contacts' in app_state['objects'])
        self.assertTrue('sales_cycles' in app_state['objects'])
        self.assertTrue('shares' in app_state['objects'])
        self.assertTrue('activities' in app_state['objects'])

        for activity in app_state['objects']['activities']:
            self.assertTrue('has_read' in activity)


class MobileStateResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_mobile_state_list = '/api/v1/mobile_state/'

        self.subscription = Subscription.objects.first()

    def test_get(self):
        mobile_state = self.api_client.get(
            self.api_path_mobile_state_list + self.subscription.service.slug + '/',
            format='json', HTTP_HOST='localhost')
        mobile_state_des = self.deserialize(mobile_state)

        self.assertHttpOK(mobile_state)
        self.assertTrue('objects' in mobile_state_des)
        self.assertTrue('constants' in mobile_state_des)
        self.assertTrue('contacts' in mobile_state_des['objects'])
        self.assertTrue('sales_cycles' in mobile_state_des['objects'])
        self.assertTrue('activities_count' in mobile_state_des['objects']['sales_cycles'][0])
        self.assertTrue('activities' in mobile_state_des['objects'])
        self.assertEqual(len(mobile_state_des['objects']['activities']), 1)
        self.assertTrue('users' in mobile_state_des['objects'])
        self.assertTrue('milestones' in mobile_state_des['objects'])



class ShareResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_share = '/api/v1/share/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_share,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_share+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.share = Share.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        resp_share = self.get_detail_des(self.share.pk)

        self.assertEqual(resp_share['share_to'], self.share.share_to.id)
        self.assertEqual(resp_share['share_from'], self.share.share_from.id)
        self.assertEqual(resp_share['contact'], self.share.contact.id)
        self.assertEqual(resp_share['note'], self.share.note)


    def test_create_share(self):
        share_to = CRMUser.objects.last()
        share_from = CRMUser.objects.first()
        contact = Contact.objects.last()
        note = 'We have meeting at 3 PM'

        post_data = {
            'share_to':share_to.id,
            'share_from':share_from.id,
            'contact':contact.id,
            'note':note
        }

        count = Share.objects.all().count()
        count_in_shares = share_to.in_shares.count()
        count_owned_shares = share_from.owned_shares.count()
        count_contact_shares = contact.share_set.count()

        self.assertHttpCreated(self.api_client.post(
             self.api_path_share, format='json', data=post_data))

        self.assertEqual(Share.objects.all().count(), count+1)
        self.assertEqual(share_to.in_shares.count(), count_in_shares+1)
        self.assertEqual(share_from.owned_shares.count(), count_owned_shares+1)
        self.assertEqual(contact.share_set.count(), count_contact_shares+1)
        # verify that subscription_id was set
        self.assertIsInstance(Share.objects.last().subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(Share.objects.last().share_to, CRMUser)
        self.assertIsInstance(Share.objects.last().share_from, CRMUser)
        self.assertIsInstance(Share.objects.last().contact, Contact)


    def test_delete_share(self):
        count = Share.objects.all().count()
        count_in_shares = CRMUser.objects.first().in_shares.count()
        count_owned_shares = CRMUser.objects.first().owned_shares.count()
        count_contact_shares = Contact.objects.first().share_set.count()
        self.assertHttpAccepted(self.api_client.delete(
             self.api_path_share + '%s/' % self.share.pk, format='json'))

        self.assertEqual(Share.objects.all().count(), count-1)
        self.assertEqual(CRMUser.objects.first().in_shares.count(), count_in_shares-1)
        self.assertEqual(CRMUser.objects.first().owned_shares.count(), count_owned_shares-1)
        self.assertEqual(Contact.objects.first().share_set.count(), count_contact_shares-1)

    def test_update_share_via_put(self):
        share = Share.objects.last()
        share_data = self.get_detail_des(share.pk)
        note_update = "_UPDATED"
        share_data['note'] += note_update
        share_data['share_to'] = 2
        share_data['contact'] = 2
        self.api_client.put(self.api_path_share + '%s/' % (self.share.pk),
                             format='json', data=share_data)

        share_last = Share.objects.last()
        self.assertEqual(share_last.note, share.note + note_update)
        self.assertEqual(share_last.share_to.id, 2)
        self.assertEqual(share_last.contact.id, 2)

    def test_create_share_with_hashtag_and_mention(self):
        share_to = CRMUser.objects.last()
        share_from = CRMUser.objects.first()
        contact = Contact.objects.last()
        note = 'We have meeting at 3 PM #sold by @[1:Bruce Wayne]'

        post_data = {
            'share_to':share_to.id,
            'share_from':share_from.id,
            'contact':contact.id,
            'note':note
        }

        count = Share.objects.all().count()
        count_in_shares = share_to.in_shares.count()
        count_owned_shares = share_from.owned_shares.count()
        count_contact_shares = contact.share_set.count()
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()

        self.assertHttpCreated(self.api_client.post(
             self.api_path_share, format='json', data=post_data))

        self.assertEqual(Share.objects.all().count(), count+1)
        self.assertEqual(share_to.in_shares.count(), count_in_shares+1)
        self.assertEqual(share_from.owned_shares.count(), count_owned_shares+1)
        self.assertEqual(contact.share_set.count(), count_contact_shares+1)
        # verify that subscription_id was set
        self.assertIsInstance(Share.objects.last().subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(Share.objects.last().share_to, CRMUser)
        self.assertIsInstance(Share.objects.last().share_from, CRMUser)
        self.assertIsInstance(Share.objects.last().contact, Contact)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text)) 

    def test_update_share_via_put_with_hashtag_and_mention(self):
        share = Share.objects.last()
        share_data = self.get_detail_des(share.pk)
        note_update = "_UPDATED #sold by @[1:Bruce Wayne]"
        share_data['note'] += note_update
        share_data['share_to'] = 2
        share_data['contact'] = 2
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        self.api_client.put(self.api_path_share + '%s/' % (self.share.pk),
                             format='json', data=share_data)

        share_last = Share.objects.last()
        self.assertEqual(share_last.note, share.note + note_update)
        self.assertEqual(share_last.share_to.id, 2)
        self.assertEqual(share_last.contact.id, 2)  
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text)) 



class CommentResourceTest(ResourceTestMixin, ResourceTestCase):
   
    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_comment = '/api/v1/comment/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_comment,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_comment+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.comment = Comment.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.comment.pk)['comment'],
            self.comment.comment
            )

    def test_create_comment_for_activity(self):
        activity = Activity.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment',
            'author_id': crmuser.pk,
            'activity_id': activity.pk
        }
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, activity.id)
        self.assertEqual(comment.content_object.__class__, Activity)
        self.assertEqual(comment.content_object, activity)
        self.assertIsInstance(comment.subscription_id, int)

    def test_create_comment_for_feedback(self):
        feedback = Feedback.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment',
            'author_id': crmuser.pk,
            'feedback_id': feedback.pk
        }
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, feedback.id)
        self.assertEqual(comment.content_object.__class__, Feedback)
        self.assertEqual(comment.content_object, feedback)
        self.assertIsInstance(comment.subscription_id, int)

    def test_create_comment_for_contact(self):
        contact = Contact.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment',
            'author_id': crmuser.pk,
            'contact_id': contact.pk
        }
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, contact.id)
        self.assertEqual(comment.content_object.__class__, Contact)
        self.assertEqual(comment.content_object, contact)
        self.assertIsInstance(comment.subscription_id, int)

    def test_create_comment_for_share(self):
        share = Share.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment',
            'author_id': crmuser.pk,
            'share_id': share.pk
        }
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, share.id)
        self.assertEqual(comment.content_object.__class__, Share)
        self.assertEqual(comment.content_object, share)
        self.assertIsInstance(comment.subscription_id, int)

    def test_delete_comment(self):
        before = Comment.objects.all().count()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_comment + '%s/' % self.comment.pk, format='json'))
        after = Comment.objects.all().count()
        # verify that one sales_cycle has been deleted.
        self.assertEqual(after, before - 1)

    def test_update_comment_via_put(self):
        # get exist product data
        comment_data = self.get_detail_des(self.comment.pk)
        # update it
        t = '_UPDATED!'
        comment_data['comment'] += t
        # PUT it
        self.api_client.put(self.api_path_comment + '%s/' % (self.comment.pk),
                            format='json', data=comment_data)
        # check
        self.assertEqual(self.get_detail_des(self.comment.pk)['comment'], self.comment.comment + t)

    def test_update_comment_via_patch(self):
        # get exist product data
        comment_comment = self.get_detail_des(self.comment.pk)['comment']
        # update it
        t = 'comment_UPDATED!'
        comment_comment += t
        # PATCH it
        self.api_client.patch(self.api_path_comment + '%s/' % (self.comment.pk),
                              format='json', data={'comment': comment_comment})
        # check
        self.assertEqual(self.get_detail_des(self.comment.pk)['comment'], comment_comment)


    def test_update_comment_via_put_with_hashtag_and_mention(self):
        # get exist product data
        comment_data = self.get_detail_des(self.comment.pk)
        # update it
        t = '_UPDATED! #sold by @[1:Bruce Wayne]'
        comment_data['comment'] += t
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        # PUT it
        self.api_client.put(self.api_path_comment + '%s/' % (self.comment.pk),
                            format='json', data=comment_data)
        # check
        self.assertEqual(self.get_detail_des(self.comment.pk)['comment'], self.comment.comment + t)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   

    def test_update_comment_via_patch(self):
        # get exist product data
        comment_comment = self.get_detail_des(self.comment.pk)['comment']
        # update it
        t = 'comment_UPDATED! #sold by @[1:Bruce Wayne]'
        comment_comment += t
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        # PATCH it
        self.api_client.patch(self.api_path_comment + '%s/' % (self.comment.pk),
                              format='json', data={'comment': comment_comment})
        # check
        self.assertEqual(self.get_detail_des(self.comment.pk)['comment'], comment_comment)   
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   

    def test_create_comment_for_activity_with_hashtag_and_mention(self):
        activity = Activity.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment  #sold by @[1:Bruce Wayne]',
            'author_id': crmuser.pk,
            'activity_id': activity.pk
        }
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment  #sold by @[1:Bruce Wayne]')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, activity.id)
        self.assertEqual(comment.content_object.__class__, Activity)
        self.assertEqual(comment.content_object, activity)
        self.assertIsInstance(comment.subscription_id, int)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   

    def test_create_comment_for_feedback_with_hashtag_and_mention(self):
        feedback = Feedback.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment  #sold by @[1:Bruce Wayne]',
            'author_id': crmuser.pk,
            'feedback_id': feedback.pk
        }
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment  #sold by @[1:Bruce Wayne]')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, feedback.id)
        self.assertEqual(comment.content_object.__class__, Feedback)
        self.assertEqual(comment.content_object, feedback)
        self.assertIsInstance(comment.subscription_id, int)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   

    def test_create_comment_for_contact_with_hashtag_and_mention(self):
        contact = Contact.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment  #sold by @[1:Bruce Wayne]',
            'author_id': crmuser.pk,
            'contact_id': contact.pk
        }
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment  #sold by @[1:Bruce Wayne]')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, contact.id)
        self.assertEqual(comment.content_object.__class__, Contact)
        self.assertEqual(comment.content_object, contact)
        self.assertIsInstance(comment.subscription_id, int)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   

    def test_create_comment_for_share_with_hashtag_and_mention(self):
        share = Share.objects.last()
        crmuser = CRMUser.objects.last()
        post_data={
            'comment': 'new test comment  #sold by @[1:Bruce Wayne]',
            'author_id': crmuser.pk,
            'share_id': share.pk
        }
        hashtag_count = HashTag.objects.all().count()
        hashtag_reference_count = HashTagReference.objects.all().count()
        mention_count = Mention.objects.all().count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_comment, format='json', data=post_data))
        comment = Comment.objects.last()
        self.assertEqual(comment.comment, 'new test comment  #sold by @[1:Bruce Wayne]')
        self.assertEqual(comment.owner, crmuser)
        self.assertEqual(comment.object_id, share.id)
        self.assertEqual(comment.content_object.__class__, Share)
        self.assertEqual(comment.content_object, share)
        self.assertIsInstance(comment.subscription_id, int)
        self.assertEqual(hashtag_count+1, HashTag.objects.all().count())
        self.assertEqual(hashtag_reference_count+1, HashTagReference.objects.all().count())
        self.assertEqual(mention_count+1, Mention.objects.all().count())
        self.assertEqual(HashTagReference.objects.last().hashtag, 
                        HashTag.objects.get(text=HashTagReference.objects.last().hashtag.text))   
  


class FilterResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_filter = '/api/v1/filter/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_filter,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_filter+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.filter = Filter.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.filter.pk)['title'],
            self.filter.title
            )

    def test_create_filter(self):
        crmuser = CRMUser.objects.last()
        post_data={
            'title': 'Filter Resource',
            'filter_text': 'Filter Resource text',
            'author_id': crmuser.pk
        }
        self.assertHttpCreated(self.api_client.post(
            self.api_path_filter, format='json', data=post_data))
        filter_obj = Filter.objects.last()
        self.assertEqual(filter_obj.title, 'Filter Resource')
        self.assertEqual(filter_obj.owner, crmuser)
        self.assertEqual(filter_obj.base, 'all')
        self
        self.assertIsInstance(filter_obj.subscription_id, int)

    def test_create_filter_with_base(self):
        crmuser = CRMUser.objects.last()
        post_data={
            'title': 'Filter Resource',
            'filter_text': 'Filter Resource text',
            'author_id': crmuser.pk,
            'base': 'cold'
        }
        self.assertHttpCreated(self.api_client.post(
            self.api_path_filter, format='json', data=post_data))
        filter_obj = Filter.objects.last()
        self.assertEqual(filter_obj.title, 'Filter Resource')
        self.assertEqual(filter_obj.owner, crmuser)
        self.assertEqual(filter_obj.base, 'cold')
        self
        self.assertIsInstance(filter_obj.subscription_id, int)


    def test_delete_filter(self):
        before = Filter.objects.all().count()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_filter + '%s/' % self.filter.pk, format='json'))
        after = Filter.objects.all().count()
        # verify that one sales_cycle has been deleted.
        self.assertEqual(after, before - 1)

    def test_update_filter_via_put(self):
        # get exist product data
        filter_data = self.get_detail_des(self.filter.pk)
        # update it
        t = '_UPDATED!'
        filter_data['title'] += t
        # PUT it
        self.api_client.put(self.api_path_filter + '%s/' % (self.filter.pk),
                            format='json', data=filter_data)
        # check
        self.assertEqual(self.get_detail_des(self.filter.pk)['title'], self.filter.title + t)

    def test_update_filter_via_patch(self):
        # get exist product data
        filter_title = self.get_detail_des(self.filter.pk)['title']
        # update it
        t = 'TITLE_UPDATED!'
        filter_title += t
        # PATCH it
        self.api_client.patch(self.api_path_filter + '%s/' % (self.filter.pk),
                              format='json', data={'title': filter_title})
        # check
        self.assertEqual(self.get_detail_des(self.filter.pk)['title'], filter_title)



class UserResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_user = '/api/v1/user/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_user,
                                                 format='json',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_user+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.user = User.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.user.pk)['email'],
            self.user.email
            )



class MilestoneResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_milestone = '/api/v1/milestone/'

        # get_list
        self.get_list_resp = self.api_client.get(self.api_path_milestone,
                                                 format='json',
                                                 charset='utf-8',
                                                 HTTP_HOST='localhost')
        self.get_list_des = self.deserialize(self.get_list_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_milestone+str(pk)+'/',
                                           format='json',
                                           charset='utf-8',
                                           HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.milestone = Milestone.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)

    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.milestone.pk)['title'],
            self.milestone.title
            )

    def test_create_milestone(self):
        crmuser = CRMUser.objects.last()
        post_data={
            'title': 'Milestone Resource',
            'color_code': '#000000',
        }
        resp = self.api_client.post(
            self.api_path_milestone, format='json', data=post_data)
        self.assertHttpCreated(resp)
        milestone_obj = Milestone.objects.last()
        self.assertEqual(milestone_obj.title, 'Milestone Resource')
        self.assertIsInstance(milestone_obj.subscription_id, int)

    def test_delete_milestone(self):
        before = Milestone.objects.all().count()
        self.assertHttpAccepted(self.api_client.delete(
            self.api_path_milestone + '%s/' % self.milestone.pk, format='json'))
        after = Milestone.objects.all().count()
        # verify that one sales_cycle has been deleted.
        self.assertEqual(after, before - 1)

    def test_update_milestone_via_put(self):
        # get exist product data
        milestone_data = self.get_detail_des(self.milestone.pk)
        # update it
        t = '_UPDATED!'
        milestone_data['title'] += t
        # PUT it
        self.api_client.put(self.api_path_milestone + '%s/' % (self.milestone.pk),
                            format='json', data=milestone_data)
        # check
        self.assertEqual(self.get_detail_des(self.milestone.pk)['title'], self.milestone.title + t)

    def test_update_milestone_via_patch(self):
        # get exist product data
        milestone_title = self.get_detail_des(self.milestone.pk)['title']
        # update it
        t = 'TITLE_UPDATED!'
        milestone_title += t
        # PATCH it
        resp = self.api_client.patch(self.api_path_milestone + '%s/' % (self.milestone.pk),
                              format='json', charset='utf-8', data={'title': milestone_title})
        # check
        self.assertHttpAccepted(resp)
        self.assertEqual(self.get_detail_des(self.milestone.pk)['title'], milestone_title)
