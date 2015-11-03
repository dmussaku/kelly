import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import ContactFactory, SalesCycleFactory, ActivityFactory
from alm_crm.models import Activity, SalesCycle

from . import TestMixin


class ActivityTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_get_activities_panel(self):
        """
        Ensure we can get proper information for dashboard panels
        """
        account2 = AccountFactory(company=self.company)
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(contact=contact, company_id=self.company.id)
        total_count = 10
        my_count = 5

        my = []
        total = []

        for i in range(total_count-my_count):
            a = ActivityFactory(sales_cycle=sales_cycle, owner=account2.user, company_id=self.company.id, deadline=timezone.now()+relativedelta.relativedelta(months=1))
            total.append(a)

        for i in range(my_count):
            a = ActivityFactory(sales_cycle=sales_cycle, owner=self.user, company_id=self.company.id, deadline=timezone.now()+relativedelta.relativedelta(months=1))
            my.append(a)
            total.append(a)

        a = my[0]
        a.deadline = timezone.now()-relativedelta.relativedelta(months=1)
        a.save()

        a = my[1]
        a.deadline = timezone.now()
        a.save()

        a = my[2]
        a.date_finished = timezone.now()
        a.save()

        a = my[3]
        a.date_finished = timezone.now()
        a.save()

        a = total[0]
        a.deadline = timezone.now()-relativedelta.relativedelta(months=1)
        a.save()

        a = total[1]
        a.deadline = timezone.now()
        a.save()

        a = total[2]
        a.date_finished = timezone.now()
        a.save()

        panel_info = Activity.get_panel_info(company_id=self.company.id, user_id=self.user.id)

        self.assertEqual(panel_info['all']['days']['total'], 10)
        self.assertEqual(panel_info['my']['days']['total'], 5)

        self.assertEqual(panel_info['all']['days']['completed'], 3)
        self.assertEqual(panel_info['my']['days']['completed'], 2)

        self.assertEqual(panel_info['all']['days']['overdue'], 2)
        self.assertEqual(panel_info['my']['days']['overdue'], 1)

    def test_change_sales_cycle_status_on_create_delete(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(contact=contact, company_id=self.company.id)

        self.assertEqual(sales_cycle.status, SalesCycle.NEW)

        a = ActivityFactory(sales_cycle=sales_cycle, owner=self.user, company_id=self.company.id)
        self.assertEqual(sales_cycle.status, SalesCycle.PENDING)

        a.delete()
        self.assertEqual(sales_cycle.status, SalesCycle.NEW)

    def test_change_sales_cycle_status_on_move(self):
        contact = ContactFactory(company_id=self.company.id)
        sales_cycle = SalesCycleFactory(contact=contact, company_id=self.company.id)

        self.assertEqual(sales_cycle.status, SalesCycle.NEW)

        a = ActivityFactory(sales_cycle=sales_cycle, owner=self.user, company_id=self.company.id)
        self.assertEqual(sales_cycle.status, SalesCycle.PENDING)

        sales_cycle2 = SalesCycleFactory(contact=contact, company_id=self.company.id)
        a.move(sales_cycle2.id)
        sales_cycle2 = SalesCycle.objects.get(id=sales_cycle2.id)

        self.assertEqual(sales_cycle.status, SalesCycle.NEW)
        self.assertEqual(sales_cycle2.status, SalesCycle.PENDING)