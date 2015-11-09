import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_crm.factories import MilestoneFactory
from alm_crm.factories import SalesCycleFactory
from alm_crm.models import Milestone, SalesCycle
from alm_user.factories import AccountFactory
from alm_company.factories import CompanyFactory

from . import TestMixin


class MilestoneTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_default_milestones(self):
        milestones = Milestone.objects.all()
        self.assertEqual(milestones.count(), 0)

        u = User(email='test@test.com')
        u.set_password('123')
        u.save()
        c = Company.build_company(name='TestCompany', subdomain='testsubdomain')
        c.save()
        a = Account(user=u, company=c)
        a.save()

        milestones = Milestone.objects.all()
        self.assertEqual(milestones.count(), 8)
        self.assertEqual(milestones.filter(is_system=1).count(),1)
        self.assertEqual(milestones.filter(is_system=2).count(),1)

    def test_create_delete(self):
        milestones = Milestone.objects.filter(company_id=self.company.id)
        milestone = Milestone(title='test', company_id=self.company.id)
        milestone.save()
        self.assertEqual(
            milestones.count()+1, 
            Milestone.objects.filter(company_id=self.company.id).count() )
        milestone.delete()
        self.assertEqual(
            milestones.count(), 
            Milestone.objects.filter(company_id=self.company.id).count() )


    