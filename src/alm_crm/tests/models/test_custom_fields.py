import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_crm.factories import MilestoneFactory
from alm_crm.models import CustomField, CustomFieldValue, SalesCycle, Contact, VCard
from django.contrib.contenttypes.models import ContentType
from alm_user.factories import AccountFactory
from alm_company.factories import CompanyFactory

from . import TestMixin


class CustomFieldTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()


    # create tests for custom fields
    # 
    def test_custom_field_create(self):
        c = self.company
        custom_field = CustomField.build_new(
            title='Test1', content_class='contact', company_id=c.id)
        custom_field.save()
        v = VCard(fn='Test')
        contact = Contact(vcard=v, company_id=c.id, owner_id=self.user.id)
        contact.save()
        custom_field_value = CustomFieldValue.build_new(
            custom_field,
            value='test_value',
            object_id=contact.id,
            save=True
            )
        









