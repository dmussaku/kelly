from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class Product(models.Model):

	title = models.CharField(_('product title'), max_length=100, blank=False)
	description = models.TextField(_('product description'))
	slug = models.CharField(_('product slug'), max_length=30, unique=True, blank=False)

	class Meta:
		verbose_name = _('product')
        db_table = settings.DB_PREFIX.format('product')

class Subscription(models.Model):

	product = models.ForeignKey(Product, related_name='subscriptions')
	user = models.ForeignKey('alm_user.User', related_name='subscriptions')
	is_active = models.BooleanField(default=True)

	class Meta:
		verbose_name = _('subscription')
		db_table = settings.DB_PREFIX.format('subscription')