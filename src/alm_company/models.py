from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime
from alm_user.models import User
from dateutil.relativedelta import relativedelta
import re


class Company(models.Model):
    name = models.CharField(max_length=100, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)
    subdomain = models.CharField(_('subdomain'), max_length=300,
                                 blank=False, unique=True)
    plan = models.ForeignKey(
        'Plan', on_delete=models.SET_NULL, blank=True, 
        null=True, related_name='companies')

    class Meta:
        verbose_name = _('company')
        db_table = settings.DB_PREFIX.format('company')

    def __unicode__(self):
        return u'%s' % self.name

    @classmethod
    def generate_subdomain(self, subdomain):
        sd = re.sub('[\W]', '', subdomain).lower()
        if sd in settings.BUSY_SUBDOMAINS:
            sd += str(1)
        i = 1
        test_sd = sd
        while(True):
            try:
                Company.objects.get(subdomain=test_sd)
            except Company.DoesNotExist:
                break
            else:
                test_sd = sd + str(i)
                i += 1
        return test_sd

    def get_users(self):
        return User.objects.filter(id__in=[a.id for a in self.accounts.all()])

    @classmethod
    def verify_company_by_subdomain(cls, company, subdomain):
        lco = company
        try:
            rco = cls.objects.get(subdomain=subdomain)
        except cls.DoesNotExist:
            rco = None
        if rco is None:
            return False
        return lco.pk == rco.pk

    @classmethod
    def build_company(cls, name=None, subdomain=None):
        subdomain = Company.generate_subdomain(name)
        company = Company(name=name, subdomain=subdomain)
        company.save()
        return company



class Plan(models.Model):
    users_num = models.IntegerField(blank=False, default=10)
    contacts_num = models.IntegerField(blank=False, default=100)
    space_per_user = models.IntegerField(blank=False, default=1)


class Payment(models.Model):
    PAYMENTS = (
        _('Visa/MasterCard'),
        _('Clearing Settlement'),
        )
    PAYMENT_TYPES = (CARD, CLEARING) = ('CARD', 'CLEARING')
    PAYMENT_OPTIONS = zip(PAYMENT_TYPES, PAYMENTS)
    description = models.CharField(max_length=5000)
    plan = models.ForeignKey(
        'Plan', related_name='payments', blank=False, null=False)
    company = models.ForeignKey(
        'Company', related_name='payments', blank=False, null=False)
    tp = models.CharField(
        max_length=20, choices=PAYMENT_OPTIONS, default=CARD)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_to_pay = models.DateTimeField(blank=True, null=True)
    date_paid = models.DateTimeField(blank=True, null=True)
    bank_statement = models.OneToOneField(
        'BankStatement', blank=True, null=True, on_delete=models.SET_NULL)

    
    def save(self, **kwargs):
        if not self.pk:
            self.date_to_pay = datetime.now()+relativedelta(months=1)
        super(self.__class__, self).save(**kwargs)
    

class BankStatement(models.Model):
    BANK_NAME = models.CharField(max_length=1000)
    CUSTOMER_NAME = models.CharField(max_length=1000)
    CUSTOMER_MAIL = models.CharField(max_length=1000)
    CUSTOMER_PHONE = models.CharField(max_length=1000)
    MERCHANT_CERT_ID = models.CharField(max_length=1000)
    MERCHANT_NAME = models.CharField(max_length=1000)
    ORDER_ID = models.CharField(max_length=1000)
    ORDER_AMOUNT = models.CharField(max_length=1000)
    ORDER_CURRENCY = models.CharField(max_length=1000)
    DEPARTMENT_MERCHANT_ID = models.CharField(max_length=1000)
    DEPARTMENT_AMOUNT = models.CharField(max_length=1000)
    MERCHANT_SIGN_TYPE = models.CharField(max_length=1000)
    CUSTOMER_SIGN_TYPE = models.CharField(max_length=1000)
    RESULTS_TIMESTAMP = models.CharField(max_length=1000)
    PAYMENT_MERCHANT_ID = models.CharField(max_length=1000)
    PAYMENT_AMOUNT = models.CharField(max_length=1000)
    PAYMENT_REFERENCE = models.CharField(max_length=1000)
    PAYMENT_APPROVAL_CODE = models.CharField(max_length=1000)
    PAYMENT_RESPONSE_CODE = models.CharField(max_length=1000)
    BANK_SIGN_CERT_ID = models.CharField(max_length=1000)
    BANK_SIGN_TYPE = models.CharField(max_length=1000)
    LETTER = models.CharField(max_length=1000)
    SIGN = models.CharField(max_length=1000)
    RAWSIGN  = models.CharField(max_length=1000)