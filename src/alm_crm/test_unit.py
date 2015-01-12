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
    Share,
    ContactList,
    SalesCycleProductStat
    )
from alm_vcard.models import VCard, Tel, Email, Org
from alm_user.models import User
from almanet.models import Subscription, Service
from alm_crm.models import GLOBAL_CYCLE_TITLE


class CRMUserTestCase(TestCase):
    fixtures=['crmusers.json', 'users.json']

    def setUp(self):
        super(CRMUserTestCase, self).setUp()
        self.crmuser=CRMUser.objects.first()

    def test_unicode(self):
        self.assertEqual(str(self.crmuser), 'Bruce Wayne')

    def test_get_billing_user(self):
        self.assertEqual(self.crmuser.get_billing_user(), User.objects.get(pk=self.crmuser.user_id))

    def test_set_supervisor(self):
        self.crmuser.set_supervisor()
        self.assertTrue(self.crmuser.is_supervisor)

    def test_unset_supervisor(self):
        self.crmuser.unset_supervisor()
        self.assertFalse(self.crmuser.is_supervisor)

    def test_get_crmusers(self):
        self.assertEqual(CRMUser.get_crmusers().last(), CRMUser.objects.last())
        user = User.objects.last()
        get_with_users = CRMUser.get_crmusers(with_users=True)
        self.assertTrue(user in get_with_users[1])


class ContactTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'feedbacks.json', 'emails.json',
                 'organizations.json', 'users.json', 'vcards.json']

    def setUp(self):
        super(ContactTestCase, self).setUp()
        self.contact1 = Contact.objects.get(pk=1)

    def test_assign_user(self):
        self.assertEqual(len(self.contact1.assignees.all()), 1)
        self.assertTrue(self.contact1.assign_user(user_id=2))
        self.assertEqual(len(self.contact1.assignees.all()), 2)
        self.assertFalse(self.contact1.assign_user(user_id=110))

    def test_assign_user_to_contacts(self):
        for pk in range(1, 4):
            self.assertEqual(
                len(Contact.objects.get(pk=pk).assignees.all()), 1)
        self.assertTrue(
            Contact.assign_user_to_contacts(user_id=2, contact_ids=[1, 2]))
        self.assertTrue(
            Contact.assign_user_to_contacts(user_id=2, contact_ids=(3, 4)))
        for pk in range(1, 4):
            c = Contact.objects.get(pk=pk)
            self.assertEqual(len(c.assignees.all()), 2)

        self.assertFalse(Contact.assign_user_to_contacts(user_id=100, contact_ids=[2,3,4]))

    def test_get_contacts_by_status(self):
        self.assertEqual(len(Contact.get_contacts_by_status(status=1)), 1)
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
        cs = Contact.filter_contacts_by_vcard(search_text='Akerke Akerke',
                                              search_params=[('fn')], order_by=[])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='Akerke',
                                              search_params=[('fn',
                                                               'icontains')], order_by=[])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='359',
                                              search_params=[('tel__value',
                                                              'icontains')], order_by=[])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='359',
                                              search_params=[('fn',
                                                              'icontains')], order_by=[])
        self.assertEqual(len(cs), 0)

    def test_get_contacts_by_last_activity_date_without_activities(self):
        contacts = Contact.get_contacts_by_last_activity_date(user_id=3)
        self.assertEqual(len(contacts), 0)

    def test_get_contacts_by_last_activity_date(self):
        user_id = 1
        self.contact1.assign_user(user_id=1)
        response = Contact.get_contacts_by_last_activity_date(user_id=1)
        self.assertEqual(list(response.all()), [self.contact1])

    def test_export_to(self):
        self.assertFalse(self.contact1.export_to(tp='doc'))
        vcard = self.contact1.export_to(tp='vcard')
        tel = 'TEL;TYPE=CELL:%s' % self.contact1.tel()
        self.assertTrue( tel in vcard )

    def test_properties(self):
        contact2 = Contact.objects.get(pk=2)
        contact2.vcard = None
        self.assertEqual(contact2.name, 'Unknown')
        self.assertEqual(contact2.tel(), 'Unknown')
        self.assertEqual(contact2.mobile(), 'Unknown')
        self.assertEqual(contact2.email(), 'Unknown')
        self.assertEqual(contact2.company(), 'Unknown organization')
        self.assertEqual(Contact.objects.get(pk=3).company(), 'Unknown organization')

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
        email = '%s<br />'%self.contact1.email()
        self.assertTrue(email in html)

    def test_add_mentions(self):
        count = Mention.objects.all().count()
        self.contact1.add_mention(user_ids=1)
        self.assertEqual(Mention.objects.all().count(), count+1)
        self.assertEqual(self.contact1.mentions.get(pk=1), Mention.objects.last())

    def test_share_contacts(self):
        share_to = CRMUser.objects.get(id=1)
        share_from = CRMUser.objects.get(id = 2)
        self.assertFalse(Contact.share_contacts(share_from = share_from, share_to = share_to, contact_ids=[]))

    def test_get_contact_detail(self):
        self.assertEqual(Contact.get_contact_detail(1), self.contact1)
        self.assertEqual(Contact.get_contact_detail(1, True), self.contact1)

    def test_import_contacts_from_vcard(self):
        count  = Contact.objects.all().count()
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'alm_crm/fixtures/nurlan.vcf')
        contacts = Contact.import_contacts_from_vcard(open(file_path, "r"))

        contact1 =  Contact.filter_contacts_by_vcard(search_text='Aslan',
                                              search_params=[('fn',
                                                               'icontains')], order_by=[])
        contact2 =  Contact.filter_contacts_by_vcard(search_text='Serik',
                                              search_params=[('fn',
                                                               'icontains')], order_by=[])
        contact3 =  Contact.filter_contacts_by_vcard(search_text='Almat',
                                              search_params=[('fn',
                                                               'icontains')], order_by=[])
        contact4 =  Contact.filter_contacts_by_vcard(search_text='Mukatayev',
                                              search_params=[('fn',
                                                               'icontains')], order_by=[])
        self.assertEqual(len(Contact.objects.all()), count+3)
        self.assertEqual(len(contact4), 3)
        self.assertTrue(contact1.first() in Contact.objects.all())
        self.assertTrue(contact2.first() in Contact.objects.all())
        self.assertTrue(contact3.first() in Contact.objects.all())


    def test_get_tp(self):
        tp_unicode = unicode(self.contact1.get_tp())
        contact_tp =  self.contact1.tp + ' type'
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
    fixtures=['products.json']

    def setUp(self):
        super(ProductTestCase, self).setUp()
        self.product = Product.objects.get(pk=1)

    def test_unicode(self):
        self.assertEqual(self.product.__unicode__(), 'p1')

    def test_get_products(self):
        self.assertEqual(len(Product.objects.all()), len(Product.get_products()))


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


    def test_unicode(self):
        self.assertEqual(self.activity1.__unicode__(), self.activity1.title)


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

        self.assertEqual(Comment.get_comments_by_context(1, Activity, 1, 0)
                         .count(), activity1.comments.count())
        self.assertEqual(Comment.get_comments_by_context(1, Activity, 1, 1)
                         .count(), 0)

    def test_add_mention(self):
        count = self.comment.mentions.count()
        self.comment.add_mention(user_ids=[2,3,4])
        self.assertEqual(self.comment.mentions.count(), count+3)


class SalesCycleTestCase(TestCase):
    fixtures = ['crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'mentions.json',
                'products.json', 'values.json', 'salescycle_product_stat']

    def setUp(self):
        super(SalesCycleTestCase, self).setUp()
        self.sc1 = SalesCycle.objects.get(pk=1)

    def get_sc(self, pk):
        return SalesCycle.objects.get(pk=pk)

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
            [4, 3, 2, 1])

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

    def test_close_sales_cycle(self):
        self.assertNotEqual(self.sc1.status, 'C')
        real_value = {
            'amount': 1000,
            'salary': None,
            'currency': None
        }
        activities_count = Activity.objects.count()

        ret = self.sc1.close(**real_value)

        self.assertIsInstance(ret, list)
        self.assertIsInstance(ret[0], SalesCycle)
        self.assertIsInstance(ret[1], Activity)
        self.assertEqual(self.sc1.status, 'C')
        self.assertEqual(self.sc1.real_value.amount, real_value['amount'])
        self.assertEqual(Activity.objects.count(), activities_count + 1)
        self.assertEqual(Activity.objects.last().feedback.status, '$')

    def test_close_sales_cycle_amount_as_string(self):
        self.assertNotEqual(self.sc1.status, 'C')
        real_value = {
            'amount': '1000',
            'salary': None,
            'currency': None
        }

        ret = self.sc1.close(**real_value)
        self.assertIsInstance(ret[0], SalesCycle)
        self.assertIsInstance(ret[1], Activity)
        self.assertEqual(self.sc1.status, 'C')
        sales_cycle = SalesCycle.objects.get(id=self.sc1.id)
        self.assertEqual(sales_cycle.real_value.amount,
                         int(real_value['amount']))

    def test_close_cycle(self):
        self.assertNotEqual(self.sc1.status, 'C')
        products_with_values = {
                "1": 15000,
                "2": 13500
        }

        ret = self.sc1.close_cycle(products_with_values)
        self.assertIsInstance(ret[0], SalesCycle)
        self.assertIsInstance(ret[1], Activity)
        self.assertEqual(self.sc1.status, 'C')
        stat1 = SalesCycleProductStat.objects.get(sales_cycle=self.sc1, product=Product.objects.get(id=1)).value
        stat2 = SalesCycleProductStat.objects.get(sales_cycle=self.sc1, product=Product.objects.get(id=2)).value
        self.assertEqual(stat1, 15000)
        self.assertEqual(stat2, 13500)



class ContactListTestCase(TestCase):
    fixtures = ['crmusers.json', 'contactlist.json', 'users.json']

    def setUp(self):
        super(self.__class__, self).setUp()
        self.contact_list = ContactList.objects.first()

    def test_create_contact_list(self):
        contact_list = ContactList(title = 'UNREGISTERED')
        self.assertEqual(contact_list.__unicode__(), 'UNREGISTERED')

    def test_add_user(self):
        crm_user = CRMUser.objects.get(id=2)
        self.contact_list.add_user(user_id=crm_user.id)
        self.assertEqual(self.contact_list.users.get(user_id=2), crm_user)
        self.assertFalse(self.contact_list.add_user(user_id=1)[0])


    def test_user_contact_lists(self):
        crm_user = CRMUser.objects.get(pk=1)
        self.assertEqual(self.contact_list,
                                crm_user.contact_list.get(id=1))


    def test_add_users(self):
        crm_user_1 = CRMUser.objects.get(id=1)
        crm_user_2 = CRMUser.objects.get(id=2)
        crm_user_3 = CRMUser.objects.get(id=3)
        self.assertEqual(self.contact_list.add_users(user_ids=[crm_user_1.id, crm_user_2.id, crm_user_3.id]), [False, True, True])
        self.assertEqual(self.contact_list.users.get(user_id=crm_user_2.id), crm_user_2)
        self.assertEqual(self.contact_list.users.get(user_id=crm_user_3.id), crm_user_3)

    def test_check_user(self):
        crm_user_1 = CRMUser.objects.get(id=1)
        crm_user_2 = CRMUser.objects.get(id=2)
        crm_user_3 = CRMUser.objects.get(id=3)
        self.contact_list.add_user(user_id=crm_user_2.id)
        self.assertTrue(self.contact_list.check_user(user_id=crm_user_1.id))
        self.assertTrue(self.contact_list.check_user(user_id=crm_user_2.id))
        self.assertFalse(self.contact_list.check_user(user_id=crm_user_3.id))

    def test_delete_user(self):
        crm_user_1 = CRMUser.objects.get(id=1)
        crm_user_2 = CRMUser.objects.get(id=2)
        crm_user_3 = CRMUser.objects.get(id=3)
        contact_list2 = ContactList(title='Test Contact list')
        contact_list2.save()
        contact_list2.add_users(user_ids=[crm_user_1.id, crm_user_2.id])
        self.assertFalse(contact_list2.delete_user(user_id=crm_user_3.id))
        self.assertTrue(contact_list2.delete_user(user_id=crm_user_2.id))
        self.assertFalse(contact_list2.delete_user(user_id=crm_user_2.id))
        self.assertTrue(contact_list2.delete_user(user_id=crm_user_1.id))
        self.assertFalse(contact_list2.delete_user(user_id=crm_user_1.id))
        self.assertEqual(contact_list2.count(), 0)

    def test_count(self):
        crm_user_1 = CRMUser.objects.get(id=1)
        crm_user_2 = CRMUser.objects.get(id=2)
        crm_user_3 = CRMUser.objects.get(id=3)
        contact_list2 = ContactList(title='Test Contact list')
        contact_list2.save()
        contact_list2.add_users(user_ids=[crm_user_1.id, crm_user_2.id, crm_user_3.id])
        self.assertEqual(contact_list2.count(), 3)


class ResourceTestMixin(object):
    fixtures = ['companies.json', 'services.json', 'users.json',
                'subscriptions.json', 'comments.json',
                'crmusers.json', 'vcards.json', 'contacts.json',
                'salescycles.json', 'activities.json', 'products.json',
                'mentions.json', 'values.json', 'emails.json', 'contactlist.json', 'share.json',
                'feedbacks.json', 'salescycle_product_stat.json']

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

        resp = self.api_client.delete(
            self.api_path_user_session+'%s/' % session_key,
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

    # def test_patch_sales_cycle_with_products(self):
    #     patch_data = {
    #         'product_ids': [1, 2, 3]
    #     }
    #     before = self.sales_cycle.products.count()

    #     resp = self.api_client.patch(
    #         self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/',
    #         format='json',
    #         data=patch_data)
    #     self.assertHttpAccepted(resp)
    #     self.assertNotEqual(before, self.sales_cycle.products.count())

    def test_replace_products(self):
        post_data = {
            "product_ids": [1, 2, 3]
        }
        before = self.sales_cycle.products.count()
        resp = self.api_client.post(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/replace_products/',
            format='json', data=post_data)
        self.assertHttpAccepted(resp)
        self.assertNotEqual(before, self.sales_cycle.products.count())

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
        put_data = {
            'value': 1000
        }

        resp = self.api_client.put(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/close/',
            format='json', data=put_data)

        self.assertHttpAccepted(resp)
        resp = self.deserialize(resp)
        self.assertTrue('activity' in resp)
        self.assertTrue('sales_cycle' in resp)
        self.assertEqual(resp['sales_cycle']['status'], 'C')
        self.assertEqual(resp['activity']['feedback'], '$')
        self.assertEqual(resp['sales_cycle']['real_value']['value'],
                         put_data['value'])

    def test_close_cycle(self):
        self.assertNotEqual(self.sales_cycle.status, 'C')
        put_data = {
            "1": 15000,
            "2": 13500
        }
        resp = self.api_client.put(
            self.api_path_sales_cycle+str(self.sales_cycle.pk)+'/close_cycle/',
            format='json', data=put_data)

        self.assertHttpAccepted(resp)
        resp = self.deserialize(resp)
        self.assertTrue('activity' in resp)
        self.assertTrue('sales_cycle' in resp)

        self.assertEqual(resp['sales_cycle']['status'], 'C')
        self.assertEqual(resp['activity']['feedback'], '$')
        stat1 = SalesCycleProductStat.objects.get(sales_cycle=self.sales_cycle, product=Product.objects.get(id=1)).value
        stat2 = SalesCycleProductStat.objects.get(sales_cycle=self.sales_cycle, product=Product.objects.get(id=2)).value
        self.assertEqual(stat1, 15000)
        self.assertEqual(stat2, 13500)



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

        self.assertEqual(resp_activity['description'], self.activity.description)
        self.assertEqual(resp_activity['author_id'], self.activity.owner.id)
        self.assertEqual(resp_activity['feedback'], self.activity.feedback.status)

    def test_create_activity_with_feedback(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': 'new activity, test_unit',
            'salescycle_id': sales_cycle.id,
            'feedback': "$"
        }
        count = Activity.objects.all().count()
        count2 = sales_cycle.rel_activities.count()
        resp = self.api_client.post(self.api_path_activity, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(Activity.objects.all().count(), count+1)
        # verify that new one has been added.
        self.assertEqual(sales_cycle.rel_activities.count(), count2 + 1)
        activity = sales_cycle.rel_activities.last()
        # verify that subscription_id was set
        self.assertIsInstance(activity.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(activity.owner, CRMUser)
        self.assertIsInstance(activity.feedback, Feedback)
        self.assertEqual(Activity.objects.last().feedback, Feedback.objects.last())

    def test_create_activity_without_sales_cycle(self):
        owner = CRMUser.objects.first()
        sales_cycle = SalesCycle.objects.get(owner=owner, is_global=True)
        post_data = {
            'author_id': owner.id,
            'description': 'new activity, test_unit'
        }
        count = Activity.objects.all().count()
        count2 = sales_cycle.rel_activities.count()
        resp = self.api_client.post(self.api_path_activity, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(Activity.objects.all().count(), count+1)
        # verify that new one has been added.
        self.assertEqual(sales_cycle.rel_activities.count(), count2 + 1)
        activity = sales_cycle.rel_activities.last()
        # verify that subscription_id was set
        self.assertIsInstance(activity.subscription_id, int)
        # verify that owner was set
        self.assertIsInstance(activity.owner, CRMUser)

    def test_create_activity_without_feedback(self):
        owner = CRMUser.objects.last()
        sales_cycle = SalesCycle.objects.first()
        post_data = {
            'author_id': owner.id,
            'description': 'new activity, test_unit',
            'salescycle_id': sales_cycle.id
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
        activity = Activity.objects.get(id = 2)
        self.assertHttpAccepted(self.api_client.delete(
        self.api_path_activity + '%s/' % activity.pk, format='json'))
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
        activity_data['feedback'] = new_feedback
        activity_data['salescycle_id'] = sales_cycle_id
        # PUT it
        self.api_client.put(self.api_path_activity + '%s/' % (activity.pk),
                            format='json', data=activity_data)
        # check
        activity_last = Activity.objects.last()
        self.assertEqual(activity_last.description, activity.description + t)
        self.assertEqual(self.get_detail_des(activity.pk)['description'], activity.description + t)

        self.assertEqual(activity_last.feedback.status, new_feedback)
        self.assertEqual(self.get_detail_des(activity.pk)['feedback'], new_feedback)

        activity_last = Activity.objects.last()
        self.assertEqual(self.get_detail_des(activity.pk)['salescycle_id'], sales_cycle_id)
        self.assertEqual(sales_cycle_id, activity_last.sales_cycle.id)

    def test_update_activity_via_patch(self):
        activity = Activity.objects.last()
        activity_data = {}
        sales_cycle_id = SalesCycle.objects.last().id
        new_feedback = "5"
        t = '_UPDATED!'
        activity_data['salescycle_id'] = sales_cycle_id
        new_description = self.get_detail_des(activity.pk)['description']+t

        self.api_client.patch(self.api_path_activity + '%s/' % (activity.pk),
                            format='json', data={'salescycle_id': sales_cycle_id})
        self.api_client.patch(self.api_path_activity + '%s/' % (activity.pk),
                            format='json', data={'feedback': new_feedback, 'description': new_description})

        activity_last = Activity.objects.last()
        self.assertEqual(activity_last.description, activity.description + t)
        self.assertEqual(self.get_detail_des(activity.pk)['description'], activity.description + t)

        self.assertEqual(activity_last.feedback.status, new_feedback)
        self.assertEqual(self.get_detail_des(activity.pk)['feedback'], new_feedback)

        activity_last = Activity.objects.last()
        self.assertEqual(self.get_detail_des(activity.pk)['salescycle_id'], sales_cycle_id)
        self.assertEqual(sales_cycle_id, activity_last.sales_cycle.id)


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

        #get list for assign contact
        self.get_list_assign_contact_resp = self.api_client.get(self.api_path_contact+'assign_contact/',
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        self.get_list_assign_contact_des = self.deserialize(self.get_list_assign_contact_resp)

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(self.api_path_contact+str(pk)+'/',
                                           format='json',
                                           HTTP_HOST='localhost')

        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.contact = Contact.objects.first()

    def test_get_list_valid_json(self):
        self.assertValidJSONResponse(self.get_list_resp)
        self.assertValidJSONResponse(self.get_list_cold_base_resp)
        self.assertValidJSONResponse(self.get_list_leads_resp)

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


    def test_get_list_non_empty(self):
        self.assertTrue(self.get_list_des['meta']['total_count'] > 0)

    def test_get_detail(self):
        self.assertEqual(
            self.get_detail_des(self.contact.pk)['id'],
            self.contact.id
            )

    def test_create_contact(self):
        post_data = {
            'status': 1,
            'tp': 'user',
            'assignees':[],
        }

        count = Contact.objects.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_contact, format='json', data=post_data))
        # verify that new one has been added.
        self.assertEqual(Contact.objects.count(), count + 1)

    def test_delete_contact(self):
        count = Contact.objects.count()

        sales_cycles = self.contact.sales_cycles.all()

        for sales_cycle in sales_cycles:
            self.assertHttpAccepted(self.api_client.delete(
                '/api/v1/sales_cycle/' + '%s/' % sales_cycle.pk, format='json'))

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
        count = self.contact.assignees.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'assign_contact/?user_id=1&contact_id=1'))

        self.assertEqual(self.contact.assignees.count(), count)

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'assign_contact/?user_id=2&contact_id=1'))

        self.assertEqual(self.contact.assignees.count(), count+1)

    def test_assign_contacts(self):
        contact1 = Contact.objects.get(pk=2)
        contact2 = Contact.objects.get(pk=3)
        contact3 = Contact.objects.get(pk=4)

        count1 = contact1.assignees.count()
        count2 = contact2.assignees.count()
        count3 = contact3.assignees.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'assign_contacts/?contact_ids=%5B2%2C3%2C4%5D&user_id=2'))

        self.assertEqual(contact1.assignees.count(), count1+1)
        self.assertEqual(contact2.assignees.count(), count2+1)
        self.assertEqual(contact3.assignees.count(), count3+1)

    def test_share_contact(self):
        count = Share.objects.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'share_contact/?contact_id=1&share_from=1&share_to=2'))

        self.assertEqual(Share.objects.count(), count+1)

        share_to = Share.objects.get(id=1).share_to
        share_from = Share.objects.get(id=1).share_from

        self.assertEqual(share_from, CRMUser.objects.get(pk=1))
        self.assertEqual(share_to, CRMUser.objects.get(pk=2))


    def test_share_contacts(self):
        count = Share.objects.count()

        self.assertHttpOK(self.api_client.get(
            self.api_path_contact+'share_contacts/?contact_ids=%5B2%2C3%2C4%5D&share_from=1&share_to=2'))

        self.assertEqual(Share.objects.count(), count+3)

        share_to = CRMUser.objects.get(id = Share.objects.get(id=1).share_to.id)
        share_from = CRMUser.objects.get(id = Share.objects.get(id=1).share_from.id)
        comment = 'comment'

        self.assertEqual(share_from, CRMUser.objects.get(pk=1))
        self.assertEqual(share_to, CRMUser.objects.get(pk=2))

    def test_search(self):
        search_text_A = Contact.filter_contacts_by_vcard(search_text='A', search_params=[('fn', 'startswith')],
                                                             order_by=[])
        srch_tx_A_ord_dc = Contact.filter_contacts_by_vcard(search_text='A', search_params=[('fn', 'startswith')],
                                                             order_by=['fn','desc'])
        srch_by_bday = Contact.filter_contacts_by_vcard(search_text='1991-09-10', search_params=['bday'],
                                                             order_by=[])
        srch_by_email = Contact.filter_contacts_by_vcard(search_text='mus', search_params=[('email__value','startswith')],
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
        user = CRMUser.objects.last()
        post_data = {
            'title': 'Mobiliuz',
            'users': [{'pk':user.pk}]
        }

        count = user.contact_list.count()
        self.assertHttpCreated(self.api_client.post(
            self.api_path_contact_list, format='json', data=post_data))
        contact_list = user.contact_list.last()
        # verify that new one has been added.
        self.assertEqual(user.contact_list.count(), count + 1)
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
        api_path_delete_user = self.api_path_contact_list+'%s/delete_user/' % self.contact_list.pk
        user_id = self.contact_list.users.first().id
        count = self.contact_list.users.all().count()
        self.assertHttpOK(self.api_client.get(api_path_delete_user+'?user_id=%d'%user_id))
        self.assertEqual(self.contact_list.users.all().count(), count-1)
        self.assertHttpOK(self.api_client.get(api_path_delete_user+'?user_id=%d'%user_id))
        self.assertEqual(self.contact_list.users.all().count(), count-1)

    def test_add_users(self):
        user = CRMUser.objects.get(pk=3)
        user3 = CRMUser.objects.get(pk=2)
        user4 = CRMUser.objects.get(pk=1)
        users = [user.pk, user3.pk, user4.pk]

        api_path_add_user = self.api_path_contact_list+'%s/add_users/' % self.contact_list.pk
        count = self.contact_list.users.all().count()

        self.assertHttpOK(self.api_client.get(api_path_add_user+'?user_ids=%s'%[user.pk]))
        self.assertEqual(self.contact_list.users.all().count(), count+1)

        self.assertHttpOK(self.api_client.get(api_path_add_user+'?user_ids=%s'%[user.pk]))
        self.assertEqual(self.contact_list.users.all().count(), count+1)

        count = count+1
        self.assertHttpOK(self.api_client.get(api_path_add_user+'?user_ids=%s'%users))
        self.assertEqual(self.contact_list.users.all().count(), count+1)

        contact_list2 = ContactList(title='HP Webcam')
        contact_list2.save()
        count = contact_list2.users.all().count()
        api_path_add_user = self.api_path_contact_list+'%s/add_users/' % contact_list2.pk

        self.assertHttpOK(self.api_client.post(api_path_add_user+'?user_ids=%s'%users))
        self.assertEqual(contact_list2.users.all().count(), count+3)

    def test_check_user(self):
        user = CRMUser.objects.get(pk=1)
        user2 = CRMUser.objects.get(pk=2)

        api_path_check_user = self.api_path_contact_list+'%s/check_user/?user_id=%s' % \
                                                            (self.contact_list.pk, user.pk)

        get_list_check_user_resp = self.api_client.get(api_path_check_user,
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        get_list_check_user_des = self.deserialize(get_list_check_user_resp)
        self.assertTrue(get_list_check_user_des['success'])

        api_path_check_user = self.api_path_contact_list+'%s/check_user/?user_id=%s' % \
                                                            (self.contact_list.pk, user2.pk)

        get_list_check_user_resp = self.api_client.get(api_path_check_user,
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        get_list_check_user_des = self.deserialize(get_list_check_user_resp)
        self.assertFalse(get_list_check_user_des['success'])

    def test_get_users(self):
        user = CRMUser.objects.get(pk=1)

        api_path_get_user = self.api_path_contact_list+'%s/users/' % \
                                                            self.contact_list.pk

        get_list_get_user_resp = self.api_client.get(api_path_get_user,
                                                                            format='json',
                                                                            HTTP_HOST='localhost')

        get_list_get_user_des = self.deserialize(get_list_get_user_resp)

        users = self.contact_list.users.all()
        self.assertEqual(get_list_get_user_des['objects'][0]['user_id'], users.first().user_id)
        self.assertEqual(get_list_get_user_des['objects'][0]['id'], users.first().id)


class AppStateResourceTest(ResourceTestMixin, ResourceTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        # login user
        self.get_credentials()

        self.api_path_app_state_list = '/api/v1/app_state/'

        # get_detail(pk)
        self.get_detail_resp = \
            lambda pk: self.api_client.get(
                self.api_path_app_state_list+str(pk)+'/',
                format='json',
                HTTP_HOST='localhost')
        self.get_detail_des = \
            lambda pk: self.deserialize(self.get_detail_resp(pk))

        self.subscription_id = Subscription.objects.first().pk

    def test_get(self):
        app_state = self.get_detail_des(self.subscription_id)
        self.assertTrue('objects' in app_state)
        self.assertTrue('users' in app_state['objects'])
        self.assertTrue('company' in app_state['objects'])
        self.assertTrue('contacts' in app_state['objects'])
        self.assertTrue('sales_cycles' in app_state['objects'])
        self.assertTrue('shares' in app_state['objects'])
        self.assertTrue('activities' in app_state['objects'])


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
        self.assertEqual(resp_share['note'], self.share.description)


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
        count_contact_shares = contact.shares.count()

        self.assertHttpCreated(self.api_client.post(
             self.api_path_share, format='json', data=post_data))

        self.assertEqual(Share.objects.all().count(), count+1)
        self.assertEqual(share_to.in_shares.count(), count_in_shares+1)
        self.assertEqual(share_from.owned_shares.count(), count_owned_shares+1)
        self.assertEqual(contact.shares.count(), count_contact_shares+1)
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
        count_contact_shares = Contact.objects.first().shares.count()
        self.assertHttpAccepted(self.api_client.delete(
             self.api_path_share + '%s/' % self.share.pk, format='json'))

        self.assertEqual(Share.objects.all().count(), count-1)
        self.assertEqual(CRMUser.objects.first().in_shares.count(), count_in_shares-1)
        self.assertEqual(CRMUser.objects.first().owned_shares.count(), count_owned_shares-1)
        self.assertEqual(Contact.objects.first().shares.count(), count_contact_shares-1)

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
        self.assertEqual(share_last.description, share.description + note_update)
        self.assertEqual(share_last.share_to.id, 2)
        self.assertEqual(share_last.contact.id, 2)


class TestCreationGlobalSalesCycle(TestCase):
    fixtures=['services.json','crmusers.json', 'users.json', 'companies.json', 'subscriptions.json',  'salescycles.json']

    def setUp(self):
        super(TestCreationGlobalSalesCycle, self).setUp()
        self.user = User.objects.first()

    def test_connect_service(self):
        crm_user = self.user.get_crmuser()
        
        with self.assertRaises(SalesCycle.DoesNotExist):
            SalesCycle.objects.get(owner=crm_user, is_global=True) 
        
        self.user.connect_service(service=Service.objects.first())
        self.assertIsInstance(crm_user, CRMUser)
        self.assertTrue(SalesCycle.objects.get(owner=crm_user, is_global=True))
        self.assertEqual(SalesCycle.objects.get(owner=crm_user, is_global=True).title, GLOBAL_CYCLE_TITLE)
        

