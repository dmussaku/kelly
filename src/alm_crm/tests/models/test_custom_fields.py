import dateutil.relativedelta as relativedelta

from django.utils import timezone
from django.test import TestCase

from alm_crm.factories import MilestoneFactory, ContactFactory
from alm_crm.models import CustomField, CustomFieldValue, SalesCycle, Contact, VCard
from django.contrib.contenttypes.models import ContentType
from alm_user.factories import AccountFactory
from alm_company.factories import CompanyFactory

from . import TestMixin


class CustomFieldTests(TestMixin, TestCase):
    def setUp(self):
        self.set_user()

    def test_custom_field_create(self):
        custom_field = CustomField.build_new(
            title='Test1', content_class=Contact, company_id=self.company.id)
        custom_field.save()
        contact = ContactFactory(owner=self.user, company_id=self.company.id)
        custom_field_value = CustomFieldValue.build_new(
            custom_field,
            value='test_value',
            object_id=contact.id,
            save=True
            )
        self.assertEqual(1, CustomFieldValue.objects.all().count())
        self.assertEqual(1, CustomField.objects.all().count())
        contact = ContactFactory(owner=self.user, company_id=self.company.id)
        self.assertEqual(1, Contact.objects.filter(custom_field_values__custom_field__isnull=True).count())
