from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import (
    ContactFactory, 
    SalesCycleFactory, 
    ActivityFactory, 
    ProductFactory,
    SalesCycleFactory,
    SalesCycleProductStatFactory,
)
from alm_vcard.factories import (
    VCardFactory,
    TelFactory,
    EmailFactory,

    )
from alm_crm.models import Contact, Milestone
from alm_vcard.models import *

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

        self.assertEqual(panel_info['all']['total'], 10)
        self.assertEqual(panel_info['my']['total'], 5)

        self.assertEqual(panel_info['all']['people'], 7)
        self.assertEqual(panel_info['my']['people'], 4)

        self.assertEqual(panel_info['all']['companies'], 3)
        self.assertEqual(panel_info['my']['companies'], 1)
        
        self.assertEqual(panel_info['all']['by_period']['days'], 10)
        self.assertEqual(panel_info['my']['by_period']['days'], 5)

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

    def test_get_products(self):
        p1 = ProductFactory(company_id=self.company.id)
        p2 = ProductFactory(company_id=self.company.id)

        c1 = ContactFactory(company_id=self.company.id, owner_id=self.user.id)
        sc1 = SalesCycleFactory(contact=c1, company_id=self.company.id, owner_id=self.user.id)
        SalesCycleProductStatFactory(sales_cycle=sc1, product=p1)

        c2 = ContactFactory(company_id=self.company.id, owner_id=self.user.id)
        sc2 = SalesCycleFactory(contact=c2, company_id=self.company.id, owner_id=self.user.id)
        SalesCycleProductStatFactory(sales_cycle=sc2, product=p1)
        SalesCycleProductStatFactory(sales_cycle=sc2, product=p2)

        self.assertEqual(len(c1.get_products()), 1)
        self.assertEqual(len(c2.get_products()), 2)

    def test_merge_contacts(self):
        v1 = VCardFactory(fn='1')
        v2 = VCardFactory(fn='2', additional_name='2')
        c1 = ContactFactory(company_id=self.company.id, owner_id=self.user.id, vcard=v1)
        sc1 = SalesCycleFactory(contact=c1, company_id=self.company.id, owner_id=self.user.id, is_global=True)
        sc1_1 = SalesCycleFactory(contact=c1, company_id=self.company.id, owner_id=self.user.id, is_global=False, title='1')
        for i in range(0,10):
            ActivityFactory(sales_cycle=sc1, owner=self.user, company_id=self.company.id)
        c2 = ContactFactory(company_id=self.company.id, owner_id=self.user.id, vcard=v2)
        sc2 = SalesCycleFactory(contact=c2, company_id=self.company.id, owner_id=self.user.id, is_global=True)
        sc2_2 = SalesCycleFactory(contact=c2, company_id=self.company.id, owner_id=self.user.id, is_global=False, title='2')
        for i in range(0,10):
            ActivityFactory(sales_cycle=sc2, owner=self.user, company_id=self.company.id)
        
        contact = c1.merge_contacts(alias_objects=[c2])
        # self.assertEqual(c1.id, None)
        # self.assertEqual(c2.id, None)
        self.assertEqual(contact.vcard.emails.count(), 6)
        self.assertEqual(contact.vcard.tels.count(), 4)
        self.assertEqual(contact.vcard.notes.count(), 1)
        self.assertEqual(contact.vcard.additional_name, '2')
        self.assertEqual(contact.sales_cycles.filter(is_global=True).count(), 1)
        self.assertEqual(contact.sales_cycles.get(is_global=True).rel_activities.count(), 20)
        self.assertEqual(contact.sales_cycles.count(), 3)

        