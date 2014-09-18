import os
import datetime
from django.utils import timezone
from django.test import TestCase
from alm_crm.models import Contact, CRMUser, Activity, SalesCycle, Feedback, Value
from alm_vcard.models import VCard


class ContactTestCase(TestCase):
    fixtures = ['crmusers.json', 'contacts.json', 'salescycles.json', 'activities.json']

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
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alm_crm/fixtures/brown.vcf')
        file_obj = open(file_path, "r").read()
        contact = Contact._upload_contacts_by_vcard(file_obj)
        self.assertEqual(contact.__class__, Contact)
        self.assertEqual(contact.vcard.__class__, VCard)
        self.assertNotEqual(contact.name, "Unknown")

    def test_upload_contacts_by_vcard_2(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alm_crm/fixtures/aliya.vcf')
        file_obj = open(file_path, "r").read()
        contact = Contact._upload_contacts_by_vcard(file_obj)
        self.assertEqual(contact.__class__, Contact)
        self.assertEqual(contact.vcard.__class__, VCard)
        addr = list(contact.vcard.adr_set.all())
        self.assertEqual(len(addr), 2)
        self.assertNotEqual(contact.name, "Unknown")

    def test_get_contacts_by_last_activity_date(self):
        struct = Contact.get_contacts_by_last_activity_date(user_id=1)

class ActivityTestCase(TestCase):
    fixtures = ['crmusers.json', 'contacts.json', 'salescycles.json', 'activities.json', 'feedbacks.json', 'values.json']

    def setUp(self):
        super(ActivityTestCase, self).setUp()
        self.salescycle = SalesCycle.objects.get(id=1)
        self.activities = Activity.objects.filter(sales_cycle_id=1)

    def test_actvities_by_contact(self):
        c = Contact.objects.get(id=1)
        a = Activity.objects.get(id=1)
        self.assertEqual(len(Activity.objects.filter(sales_cycle__contact_id=c.id)), len(a.get_activities_by_contact(c.id)))

    def test_set_feedback(self):
        self.assertNotEqual(0, len(Activity.objects.filter(sales_cycle_id=1)))
        self.assertNotEqual(0, len(Feedback.objects.all()))
        a = Activity(title='t6', description='d6', when=timezone.now(), sales_cycle_id=1, author_id=1)
        a.save()
        self.assertEqual(a,Activity.objects.get(id=a.id))
        self.assertEqual(0, len(Feedback.objects.filter(id=a.id)))
        f = Feedback(feedback='feedback8', status="W", date_created=timezone.now(), date_edited=timezone.now(), activity=a)
        f.save()
        self.assertEqual(f, Feedback.objects.get(id=f.id))
        a.set_feedback(f, True)
        self.assertEqual(a,f.activity)

    def test_get_activities_by_salescycle(self):
        a=Activity()
        if (len(self.activities)==len(a.get_activities_by_salescycle(1,0,0))):
            self.assertEqual(len(set(self.activities).intersection(a.get_activities_by_salescycle(1,0,0))), len(self.activities))
        else:
            return False


    def test_get_mentioned_activites_of(self):
        pass

    def test_get_activity_details(self):
        pass

    def test_number_of_activities_by_day(self):
        pass


