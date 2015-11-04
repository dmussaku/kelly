import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import SalesCycleFactory, ContactFactory, ActivityFactory
from alm_crm.models import SalesCycle, Milestone

from . import TestMixin


class SalesCycleTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_get_sales_cycle_panel(self):
        """
        Ensure we can get proper information for dashboard panels
        """
        account2 = AccountFactory(company=self.company)
        total_count = 10
        my_count = 5

        contact = ContactFactory(company_id=self.company.id)
        success_milestone = Milestone.objects.get(is_system=1)
        milestone = Milestone.objects.filter(is_system=0)[0]
        milestone2 = Milestone.objects.filter(is_system=0)[1]

        my_scs = []
        total_scs = []

        for i in range(total_count-my_count):
            sc = SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)
            total_scs.append(sc)

        for i in range(my_count):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            my_scs.append(sc)
            total_scs.append(sc)

        sc1 = my_scs[0]
        sc1.change_milestone(self.user, success_milestone.id, self.company.id)

        sc1 = my_scs[1]
        sc1.change_milestone(self.user, milestone.id, self.company.id)

        sc1 = my_scs[2]
        sc1.change_milestone(self.user, milestone.id, self.company.id)

        sc1 = my_scs[3]
        ActivityFactory(sales_cycle=sc1, owner=self.user, company_id=self.company.id)

        sc1 = total_scs[0]
        sc1.change_milestone(self.user, success_milestone.id, self.company.id)

        sc1 = total_scs[1]
        sc1.change_milestone(self.user, milestone.id, self.company.id)

        sc1 = total_scs[2]
        sc1.change_milestone(self.user, milestone2.id, self.company.id)

        sc1 = total_scs[2]
        ActivityFactory(sales_cycle=sc1, owner=self.user, company_id=self.company.id)

        panel_info = SalesCycle.get_panel_info(company_id=self.company.id, user_id=self.user.id)

        self.assertEqual(panel_info['new_sales_cycles']['all']['days'], 3)
        self.assertEqual(panel_info['new_sales_cycles']['my']['days'], 1)

        self.assertEqual(panel_info['successful_sales_cycles']['all']['days'], 2)
        self.assertEqual(panel_info['successful_sales_cycles']['my']['days'], 1)

        self.assertEqual(panel_info['open_sales_cycles']['all']['days']['total'], 5)
        self.assertEqual(panel_info['open_sales_cycles']['my']['days']['total'], 3)

        self.assertEqual(panel_info['open_sales_cycles']['all']['days']['by_milestones'][milestone.id], 3)
        self.assertEqual(panel_info['open_sales_cycles']['my']['days']['by_milestones'][milestone.id], 2)

        self.assertEqual(panel_info['open_sales_cycles']['all']['days']['by_milestones'][milestone2.id], 1)
        self.assertEqual(panel_info['open_sales_cycles']['my']['days']['by_milestones'][milestone2.id], 0)        

    # def test_get_active_deals(self):
    #     """
    #     Ensure we can get active deals for dashboard
    #     """
    #     account2 = AccountFactory(company=self.company)
    #     total_count = 10
    #     my_count = 5

    #     contact = ContactFactory(company_id=self.company.id)
    #     milestone = Milestone.objects.filter(is_system=0)[0]
    #     milestone2 = Milestone.objects.filter(is_system=0)[1]

    #     my_scs = []
    #     total_scs = []

    #     for i in range(total_count-my_count):
    #         sc = SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)
    #         total_scs.append(sc)

    #     for i in range(my_count):
    #         sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
    #         my_scs.append(sc)
    #         total_scs.append(sc)

    def test_change_milestone(self):
        contact = ContactFactory(company_id=self.company.id)
        success_milestone = Milestone.objects.get(is_system=1)
        fail_milestone = Milestone.objects.get(is_system=2)
        milestone = Milestone.objects.filter(is_system=0)[0]

        sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
        self.assertEqual(sc.milestone, None)
        self.assertEqual(sc.status, SalesCycle.NEW)

        sc.change_milestone(self.user, milestone.id, self.company.id)
        self.assertEqual(sc.milestone.id, milestone.id)
        self.assertEqual(sc.status, SalesCycle.PENDING)
        self.assertEqual(sc.log.count(), 1)

        sc.change_milestone(self.user, success_milestone.id, self.company.id)
        self.assertEqual(sc.milestone.id, success_milestone.id)
        self.assertEqual(sc.status, SalesCycle.SUCCESSFUL)
        self.assertEqual(sc.log.count(), 2)

        sc.change_milestone(self.user, fail_milestone.id, self.company.id)
        self.assertEqual(sc.milestone.id, fail_milestone.id)
        self.assertEqual(sc.status, SalesCycle.FAILED)
        self.assertEqual(sc.log.count(), 3)

    def test_get_all(self):
        """
        Ensure we can get all sales cycles
        """
        contact = ContactFactory(company_id=self.company.id)
        for i in range(10):
            SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)

        self.assertEqual(SalesCycle.get_all(company_id=self.company.id).count(), 10)

    def test_get_all_new(self):
        """
        Ensure we can get all new sales cycles
        """
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.filter(is_system=0)[0]
        scs = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_new_all(company_id=self.company.id).count(), 7)

    def test_get_all_pending(self):
        """
        Ensure we can get all pending sales cycles
        """
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.filter(is_system=0)[0]
        scs = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_pending_all(company_id=self.company.id).count(), 3)

    def test_get_all_successful(self):
        """
        Ensure we can get all successful sales cycles
        """
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.get(is_system=1)
        scs = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_successful_all(company_id=self.company.id).count(), 3)

    def test_get_all_failed(self):
        """
        Ensure we can get all failed sales cycles
        """
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.get(is_system=2)
        scs = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_failed_all(company_id=self.company.id).count(), 3)

    def test_get_all_my(self):
        """
        Ensure we can get my sales cycles
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        for i in range(10):
            SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)

        for i in range(3):
            SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)

        self.assertEqual(SalesCycle.get_my(company_id=self.company.id, user_id=self.user.id).count(), 10)
        self.assertEqual(SalesCycle.get_my(company_id=self.company.id, user_id=account2.user.id).count(), 3)

    def test_get_my_new(self):
        """
        Ensure we can get my new sales cycles
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.filter(is_system=0)[0]
        scs = []
        scs2 = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        for i in range(3):
            sc = SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)
            scs2.append(sc)

        for i in range(2):
            scs2[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_new_my(company_id=self.company.id, user_id=self.user.id).count(), 7)
        self.assertEqual(SalesCycle.get_new_my(company_id=self.company.id, user_id=account2.user.id).count(), 1)

    def test_get_my_pending(self):
        """
        Ensure we can get my pending sales cycles
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.filter(is_system=0)[0]
        scs = []
        scs2 = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        for i in range(3):
            sc = SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)
            scs2.append(sc)

        for i in range(2):
            scs2[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_pending_my(company_id=self.company.id, user_id=self.user.id).count(), 3)
        self.assertEqual(SalesCycle.get_pending_my(company_id=self.company.id, user_id=account2.user.id).count(), 2)

    def test_get_my_successful(self):
        """
        Ensure we can get my successful sales cycles
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.get(is_system=1)
        scs = []
        scs2 = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        for i in range(3):
            sc = SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)
            scs2.append(sc)

        for i in range(2):
            scs2[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_successful_my(company_id=self.company.id, user_id=self.user.id).count(), 3)
        self.assertEqual(SalesCycle.get_successful_my(company_id=self.company.id, user_id=account2.user.id).count(), 2)

    def test_get_my_failed(self):
        """
        Ensure we can get my failed sales cycles
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        milestone = Milestone.objects.get(is_system=2)
        scs = []
        scs2 = []
        for i in range(10):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            scs.append(sc)

        for i in range(3):
            scs[i].change_milestone(self.user, milestone.id, self.company.id)

        for i in range(3):
            sc = SalesCycleFactory(contact=contact, owner=account2.user, company_id=self.company.id)
            scs2.append(sc)

        for i in range(2):
            scs2[i].change_milestone(self.user, milestone.id, self.company.id)

        self.assertEqual(SalesCycle.get_failed_my(company_id=self.company.id, user_id=self.user.id).count(), 3)
        self.assertEqual(SalesCycle.get_failed_my(company_id=self.company.id, user_id=account2.user.id).count(), 2)
    