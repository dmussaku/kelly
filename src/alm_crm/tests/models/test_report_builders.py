from django.test import TestCase

from alm_user.factories import AccountFactory
from alm_crm.factories import SalesCycleFactory, ContactFactory, ProductFactory
from alm_crm.models import SalesCycle, Milestone
from alm_crm.utils import report_builders

from . import TestMixin


class ReportBuildersTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_build_funnel(self):
        """
        Ensure we can build funnel
        """
        account2 = AccountFactory(company=self.company)
        total_count = 10

        contact = ContactFactory(company_id=self.company.id)
        fail_milestone = Milestone.objects.get(is_system=2)
        success_milestone = Milestone.objects.get(is_system=1)
        milestone = Milestone.objects.filter(is_system=0)[0]
        milestone2 = Milestone.objects.filter(is_system=0)[1]

        total_scs = []
        data = {}

        for i in range(total_count):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            total_scs.append(sc)

        sc = total_scs[0]
        sc.change_milestone(success_milestone.id, self.user.id, self.company.id)

        sc = total_scs[1]
        sc.change_milestone(milestone.id, self.user.id, self.company.id)

        sc = total_scs[2]
        sc.change_milestone(milestone2.id, self.user.id, self.company.id)

        sc = total_scs[3]
        sc.change_milestone(milestone2.id, self.user.id, self.company.id)

        sc = total_scs[4]
        sc.change_milestone(fail_milestone.id, self.user.id, self.company.id)

        report = report_builders.build_funnel(self.company.id, data)

        self.assertEqual(report['report_name'], 'funnel')
        self.assertTrue(report.has_key('total'))
        self.assertEqual(report['total'], 10)
        self.assertTrue(report.has_key('undefined'))
        self.assertEqual(report['undefined'], 5)
        self.assertTrue(report.has_key('funnel'))
        self.assertEqual(len(report['funnel'][milestone.id]), 5)
        self.assertEqual(len(report['funnel'][milestone2.id]), 4)
        self.assertEqual(len(report['funnel'][success_milestone.id]), 1)
        self.assertEqual(len(report['funnel'][fail_milestone.id]), 1)


    def test_build_realtime_funnel(self):
        """
        Ensure we can build realtime funnel
        """
        account2 = AccountFactory(company=self.company)
        total_count = 10

        contact = ContactFactory(company_id=self.company.id)
        fail_milestone = Milestone.objects.get(is_system=2)
        success_milestone = Milestone.objects.get(is_system=1)
        milestone = Milestone.objects.filter(is_system=0)[0]
        milestone2 = Milestone.objects.filter(is_system=0)[1]

        total_scs = []
        data = {}

        for i in range(total_count):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            total_scs.append(sc)

        sc = total_scs[0]
        sc.change_milestone(success_milestone.id, self.user.id, self.company.id)

        sc = total_scs[1]
        sc.change_milestone(milestone.id, self.user.id, self.company.id)

        sc = total_scs[2]
        sc.change_milestone(milestone2.id, self.user.id, self.company.id)

        sc = total_scs[3]
        sc.change_milestone(milestone2.id, self.user.id, self.company.id)

        sc = total_scs[4]
        sc.change_milestone(fail_milestone.id, self.user.id, self.company.id)

        report = report_builders.build_realtime_funnel(self.company.id, data)

        self.assertEqual(report['report_name'], 'realtime_funnel')
        self.assertTrue(report.has_key('total'))
        self.assertEqual(report['total'], 10)
        self.assertTrue(report.has_key('undefined'))
        self.assertEqual(report['undefined'], 5)
        self.assertTrue(report.has_key('funnel'))
        self.assertEqual(len(report['funnel'][milestone.id]), 1)
        self.assertEqual(len(report['funnel'][milestone2.id]), 2)
        self.assertEqual(len(report['funnel'][success_milestone.id]), 1)
        self.assertEqual(len(report['funnel'][fail_milestone.id]), 1)

    def test_build_product_report(self):
        """
        Ensure we can build product report
        """
        account2 = AccountFactory(company=self.company)
        total_count = 10

        contact = ContactFactory(company_id=self.company.id)
        success_milestone = Milestone.objects.get(is_system=1)
        milestone = Milestone.objects.filter(is_system=0)[0]

        p1 = ProductFactory(owner=self.user, company_id=self.company.id)
        p2 = ProductFactory(owner=self.user, company_id=self.company.id)

        total_scs = []
        data = {}

        for i in range(total_count):
            sc = SalesCycleFactory(contact=contact, owner=self.user, company_id=self.company.id)
            total_scs.append(sc)

        sc = total_scs[0]
        sc = sc.change_products(product_ids=[p1.id], user_id=self.user.id, company_id=self.company.id)
        sc = sc.change_milestone(success_milestone.id, self.user.id, self.company.id)
        sc = sc.succeed(stats={p1.id: 500}, user_id=self.user.id, company_id=self.company.id)

        sc = total_scs[1]
        sc = sc.change_products(product_ids=[p1.id], user_id=self.user.id, company_id=self.company.id)
        sc = sc.change_milestone(milestone.id, self.user.id, self.company.id)

        sc = total_scs[2]
        sc = sc.change_products(product_ids=[p1.id, p2.id], user_id=self.user.id, company_id=self.company.id)
        sc = sc.change_milestone(success_milestone.id, self.user.id, self.company.id)
        sc = sc.succeed(stats={p1.id: 700, p2.id: 100}, user_id=self.user.id, company_id=self.company.id)

        sc = total_scs[3]
        sc = sc.change_products(product_ids=[p2.id], user_id=self.user.id, company_id=self.company.id)
        sc = sc.change_milestone(success_milestone.id, self.user.id, self.company.id)
        sc = sc.succeed(stats={p2.id: 200}, user_id=self.user.id, company_id=self.company.id)

        report = report_builders.build_product_report(self.company.id, data)

        self.assertEqual(report['report_name'], 'product_report')
        self.assertTrue(report.has_key('products'))
        self.assertTrue(report['products'][p1.id].has_key('earned_money'))
        self.assertEqual(report['products'][p1.id]['earned_money'], 1200)
        self.assertTrue(report['products'][p1.id].has_key('total_cycles'))
        self.assertEqual(report['products'][p1.id]['total_cycles'], 3)
        self.assertTrue(report['products'][p1.id].has_key('by_milestone'))
        self.assertEqual(len(report['products'][p1.id]['by_milestone'][success_milestone.id]), 2)
        self.assertEqual(len(report['products'][p1.id]['by_milestone'][milestone.id]), 1)
        self.assertTrue(report['products'][p2.id].has_key('earned_money'))
        self.assertEqual(report['products'][p2.id]['earned_money'], 300)
        self.assertTrue(report['products'][p2.id].has_key('total_cycles'))
        self.assertEqual(report['products'][p2.id]['total_cycles'], 2)
        self.assertTrue(report['products'][p2.id].has_key('by_milestone'))
        self.assertEqual(len(report['products'][p2.id]['by_milestone'][success_milestone.id]), 2)
        self.assertEqual(len(report['products'][p2.id]['by_milestone'][milestone.id]), 0)
