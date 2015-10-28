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


class Subscription(models.Model):
    # global_sales_cycle_id = models.IntegerField(_('sales_cycle_id'), null=True, blank=True)
    user = models.ForeignKey('alm_user.User', related_name='subscriptions', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)
        # if hasattr(self, 'user') and self.user is not None:
        #     if not hasattr(self, 'organization') or not self.organization:
        #         self.organization = self.user.get_company()

    class Meta:
        verbose_name = _('subscription')
        db_table = settings.DB_PREFIX.format('subscription')

    def get_home_url(self):
        url_key = '{}_home'.format(settings.DEFAULT_SERVICE)
        return almanet_reverse(
            url_key,
            subdomain=self.organization.subdomain,
            kwargs={'service_slug': self.service.slug.lower()})

    def __unicode__(self):
        output = "Subscription object "
        if self.id:
            output += "id= %s" % self.id
        try:
            output += " for company %s" % self.company.name
        except:
            pass 
        return output

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
    name_ru = models.CharField(max_length=100)
    description_ru = models.CharField(max_length=1000)
    name_en = models.CharField(max_length=100)
    description_en = models.CharField(max_length=1000)
    price_kzt = models.IntegerField(blank=False, default=0)
    price_usd = models.IntegerField(blank=False, default=0)
    users_num = models.IntegerField(blank=False, default=10)
    contacts_num = models.IntegerField(blank=False, default=100)
    space_per_user = models.IntegerField(blank=False, default=1)
    pic = models.CharField(max_length=100, blank=True)
    sm_pic = models.CharField(max_length=100, blank=True)


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
    bank_name = models.CharField(max_length=1000)
    customer_name = models.CharField(max_length=1000)
    customer_mail = models.CharField(max_length=1000)
    customer_phone = models.CharField(max_length=1000)
    merchant_cert_id = models.CharField(max_length=1000)
    merchant_name = models.CharField(max_length=1000)
    order_id = models.CharField(max_length=1000)
    order_amount = models.CharField(max_length=1000)
    order_currency = models.CharField(max_length=1000)
    department_merchant_id = models.CharField(max_length=1000)
    department_amount = models.CharField(max_length=1000)
    merchant_sign_type = models.CharField(max_length=1000)
    customer_sign_type = models.CharField(max_length=1000)
    results_timestamp = models.CharField(max_length=1000)
    payment_merchant_id = models.CharField(max_length=1000)
    payment_amount = models.CharField(max_length=1000)
    payment_reference = models.CharField(max_length=1000)
    payment_approval_code = models.CharField(max_length=1000)
    payment_response_code = models.CharField(max_length=1000)
    bank_sign_cert_id = models.CharField(max_length=1000)
    bank_sign_type = models.CharField(max_length=1000)
    letter = models.CharField(max_length=1000)
    sign = models.CharField(max_length=1000)
    rawsign  = models.CharField(max_length=1000)