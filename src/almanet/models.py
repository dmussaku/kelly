from almanet.url_resolvers import reverse as almanet_reverse
from almanet.utils.metaprogramming import SerializableModel
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class Service(models.Model):

    title = models.CharField(_('service title'), max_length=100, blank=False)
    description = models.TextField(_('service description'), null=True)
    slug = models.CharField(
        _('service slug'), max_length=30, unique=True, blank=False)

    class Meta:
        verbose_name = _('service')
        db_table = settings.DB_PREFIX.format('service')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super(Service, self).save(**kwargs)


class Subscription(models.Model):
    # global_sales_cycle_id = models.IntegerField(_('sales_cycle_id'), null=True, blank=True)
    service = models.ForeignKey(Service, related_name='subscriptions')
    user = models.ForeignKey('alm_user.User', related_name='subscriptions')
    organization = models.ForeignKey(
        'alm_company.Company', related_name='subscriptions')
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)
    plan = models.ForeignKey('Plan', related_name='subscriptions', 
        null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)
        if hasattr(self, 'user') and self.user is not None:
            if not hasattr(self, 'organization') or not self.organization:
                self.organization = self.user.get_company()

    class Meta:
        verbose_name = _('subscription')
        db_table = settings.DB_PREFIX.format('subscription')

    def get_home_url(self):
        url_key = '{}_home'.format(settings.DEFAULT_SERVICE)
        return almanet_reverse(
            url_key,
            subdomain=self.organization.subdomain,
            kwargs={'service_slug': self.service.slug.lower()})

class SubscriptionObject(models.Model):
    # subscription_id = models.IntegerField(_('subscription id'),
    #                                       null=True, blank=True)
    company_id = models.IntegerField(_('company_id'), null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)
    
    class Meta:
        abstract = True

    def save(self, **kwargs):
        super(SubscriptionObject, self).save(**kwargs)


class SerializableSubscriptionObject(SubscriptionObject, SerializableModel):
    
    class Meta:
        abstract = True


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
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

    CURRENCY_TYPES = (KZT, USD) = ('KZT', 'USD')
    CURRENCIES = (
        _('KZT'),
        _('USD'),
        )
    CURRENCY_OPTIONS = zip(CURRENCY_TYPES, CURRENCIES)
    EPAY_CURRENCY_DICT = {'KZT':'398', 'USD':'840'}
    description = models.CharField(max_length=5000)
    amount = models.IntegerField(blank=False, null=False)
    currency = models.CharField(
        max_length=3, choices=CURRENCY_OPTIONS, default=KZT)
    plan = models.ForeignKey(
        'Plan', related_name='payments', blank=False, null=False)
    subscription = models.ForeignKey(
        'Subscription', related_name='payments')
    plan = models.ForeignKey(
        'Plan', related_name='payments')
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