import dateutil.relativedelta as relativedelta

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from alm_crm.factories import FilterFactory, ContactFactory
from alm_crm.models import Filter

from . import TestMixin


class CustomFieldTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_apply_filter(self):
        ContactFactory(vcard__fn='John', owner_id=self.user.id, company_id=self.company.id)
        ContactFactory(vcard__fn='Mike', owner_id=self.user.id, company_id=self.company.id)
        f = FilterFactory(filter_text='John', owner_id=self.user.id, company_id=self.company.id)
        data = f.apply(company_id=self.company.id, user_id=self.user.id)

        self.assertEqual(len(data), 1)
