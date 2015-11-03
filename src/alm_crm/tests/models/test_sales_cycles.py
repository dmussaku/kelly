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
        sc1.milestone = success_milestone
        sc1.save()

        sc1 = my_scs[1]
        sc1.milestone = milestone
        sc1.save()

        sc1 = my_scs[2]
        sc1.milestone = milestone
        sc1.save()

        sc1 = my_scs[3]
        ActivityFactory(sales_cycle=sc1, owner=self.user, company_id=self.company.id)

        sc1 = total_scs[0]
        sc1.milestone = success_milestone
        sc1.save()

        sc1 = total_scs[1]
        sc1.milestone = milestone
        sc1.save()

        sc1 = total_scs[2]
        sc1.milestone = milestone2
        sc1.save()

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

    def test_get_new_all(self):
        """
        Ensure we can get all new sales cycles
        """
