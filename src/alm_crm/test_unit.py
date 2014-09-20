import os
from django.test import TestCase
from alm_crm.models import Contact, CRMUser, Activity
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
        contact = Contact.upload_contacts(upload_type='vcard', file_obj=file_obj)
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
        contact = Contact._upload_contacts_by_vcard(file_obj)
        cs = Contact.filter_contacts_by_vcard(search_text='Aliya', 
                                              search_params=[('fn')])
        self.assertEqual(len(cs), 1)
        cs = Contact.filter_contacts_by_vcard(search_text='liya', 
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
