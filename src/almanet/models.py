from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from almanet.url_resolvers import reverse as almanet_reverse
from almanet.utils.metaprogramming import SerializableModel
from django.db.models import signals
from django.utils import timezone
from datetime import datetime


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
<<<<<<< Updated upstream
=======
        if not self.subscription_id and self.owner:
            self.subscription_id = self.owner.subscription_id
            with open('./in', 'a') as f:
                f.write('SubscriptionObject::save {}-{}::{}\n'.format(
                    self.owner.get_billing_user().vcard.fn,
                    self.owner.get_billing_user().pk, self.owner.subsription_id))
>>>>>>> Stashed changes
        super(SubscriptionObject, self).save(**kwargs)


class SerializableSubscriptionObject(SubscriptionObject, SerializableModel):
    
    class Meta:
        abstract = True
