from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import ContactFactory
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
