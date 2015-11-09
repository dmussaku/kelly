from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import ContactFactory, SalesCycleFactory, ActivityFactory
from alm_crm.models import Contact, Milestone

from . import TestMixin


class ContactTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_get_contacts_panel(self):
        """
        Ensure we can get proper information for dashboard panels
        """
        account2 = AccountFactory(company=self.company)
        total_count = 10
        my_count = 5

        my = []
        total = []

        for i in range(total_count-my_count):
            sc = ContactFactory(owner=account2.user, company_id=self.company.id)
            total.append(sc)

        for i in range(my_count):
            sc = ContactFactory(owner=self.user, company_id=self.company.id)
            my.append(sc)
            total.append(sc)

        c = my[0]
        c.tp = Contact.COMPANY_TP
        c.save()

        c = total[0]
        c.tp = Contact.COMPANY_TP
        c.save()

        c = total[1]
        c.tp = Contact.COMPANY_TP
        c.save()

        panel_info = Contact.get_panel_info(company_id=self.company.id, user_id=self.user.id)

        self.assertEqual(panel_info['all']['days']['total'], 10)
        self.assertEqual(panel_info['my']['days']['total'], 5)

        self.assertEqual(panel_info['all']['days']['people'], 7)
        self.assertEqual(panel_info['my']['days']['people'], 4)

        self.assertEqual(panel_info['all']['days']['companies'], 3)
        self.assertEqual(panel_info['my']['days']['companies'], 1)

    def test_get_all(self):
        account2 = AccountFactory(company=self.company)

        for i in range(5):
            ContactFactory(company_id=self.company.id, owner_id=self.user.id)

        for i in range(3):
            ContactFactory(company_id=self.company.id, owner_id=account2.user.id)
        
        contacts = Contact.get_all(company_id=self.company.id)
        self.assertEqual(contacts.count(), 8)

    def test_get_lead_base(self):
        account2 = AccountFactory(company=self.company)

        for i in range(5):
            ContactFactory(company_id=self.company.id, owner_id=self.user.id)

        for i in range(3):
            contact = ContactFactory(company_id=self.company.id, owner_id=account2.user.id)
            sales_cycle = SalesCycleFactory(contact=contact, company_id=self.company.id)
            ActivityFactory(sales_cycle=sales_cycle, owner=self.user, company_id=self.company.id)
        
        contacts = Contact.get_lead_base(company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(contacts.count(), 3)

    def test_get_cold_base(self):
        account2 = AccountFactory(company=self.company)

        for i in range(5):
            ContactFactory(company_id=self.company.id, owner_id=self.user.id)

        for i in range(3):
            contact = ContactFactory(company_id=self.company.id, owner_id=account2.user.id)
            sales_cycle = SalesCycleFactory(contact=contact, company_id=self.company.id)
            ActivityFactory(sales_cycle=sales_cycle, owner=self.user, company_id=self.company.id)
        
        contacts = Contact.get_cold_base(company_id=self.company.id, user_id=self.user.id)
        self.assertEqual(contacts.count(), 5)
