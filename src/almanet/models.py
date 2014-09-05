from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify

class Product(models.Model):

    title = models.CharField(_('product title'), max_length=100, blank=False)
    description = models.TextField(_('product description'))
    slug = models.CharField(
        _('product slug'), max_length=30, unique=True, blank=False)

    class Meta:
        verbose_name = _('product')
        db_table = settings.DB_PREFIX.format('product')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super(Product, self).save(**kwargs)


class Subscription(models.Model):

    product = models.ForeignKey(Product, related_name='subscriptions')
    user = models.ForeignKey('alm_user.User', related_name='subscriptions')
    organization = models.ForeignKey(
        'alm_company.Company', related_name='subscriptions')
    is_active = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)
        if hasattr(self, 'user') and not self.user is None:
            self.organization = self.user.get_company()

    class Meta:
        verbose_name = _('subscription')
        db_table = settings.DB_PREFIX.format('subscription')


