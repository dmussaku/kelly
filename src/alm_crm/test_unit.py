import datetime
from django.test import TestCase
from alm_crm.models import Contact, CRMUser


class ContactTestCase(TestCase):
    fixtures = ['crmusers.json', 'contacts.json']

    def setUp(self):
        super(ContactTestCase, self).setUp()
        self.contact_1 = Contact.objects.get(pk=1)

    def test_assign_user(self):
        self.assertEqual(len(self.contact_1.assignees.all()), 0)
        self.assertTrue(self.contact_1.assign_user(user_id=1))
        self.assertEqual(len(self.contact_1.assignees.all()), 1)

    def test_assign_user_to_contacts(self):
        for pk in range(1, 4):
            self.assertEqual(len(Contact.objects.get(pk=pk).assignees.all()), 0)
        self.assertTrue(Contact.assign_user_to_contacts(user_id=1, contact_ids=[1,2]))
        self.assertTrue(Contact.assign_user_to_contacts(user_id=1, contact_ids=(3,4)))
        for pk in range(1, 4):
            c = Contact.objects.get(pk=pk)
            self.assertEqual(len(c.assignees.all()), 1)

    def test_get_contacts_by_status(self):
        self.assertEqual(len(Contact.get_contacts_by_status(status=1)), 2)
        self.assertEqual(len(Contact.get_contacts_by_status(status=1, limit=1)), 1)

    def test_get_cold_base(self):
        self.assertEqual(len(Contact.get_cold_base()), 1)

