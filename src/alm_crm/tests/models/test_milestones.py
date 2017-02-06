import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_crm.factories import MilestoneFactory
from alm_crm.factories import SalesCycleFactory
from alm_crm.models import Milestone, SalesCycle
from alm_user.factories import AccountFactory, UserFactory
from alm_company.factories import CompanyFactory

from . import TestMixin


class MilestoneTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_default_milestones(self):

        u = UserFactory()
        c = CompanyFactory()
        a = AccountFactory(
            user=u, company=c)

        milestones = Milestone.objects.all()
        self.assertEqual(milestones.count(), 8)
        self.assertEqual(milestones.filter(is_system=1).count(),1)
        self.assertEqual(milestones.filter(is_system=2).count(),1)

    def test_create_delete(self):
        milestones = Milestone.objects.filter(company_id=self.company.id)
        milestone_count = milestones.count()
        milestone = Milestone(title='test', company_id=self.company.id)
        milestone.save()
        self.assertEqual(
            milestone_count+1, 
            Milestone.objects.filter(company_id=self.company.id).count() )
        milestone.delete()
        self.assertEqual(
            milestone_count, 
            Milestone.objects.filter(company_id=self.company.id).count() )


    