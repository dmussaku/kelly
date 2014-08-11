from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, UserManager as contrib_user_manager)
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from timezone_field import TimeZoneField


class UserManager(contrib_user_manager):
    """
    had to override just because of missing username field in model
    """
    def create_user(self, first_name, last_name, email, password):
        user = User(first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):

    #REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'email'
    first_name = models.CharField(_('first name'), max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    email = models.EmailField(_('email address'), unique=True, blank=False)
    is_active = models.BooleanField(_('active'), default=True)

    timezone = TimeZoneField(default='Asia/Almaty')

    company = models.ManyToManyField('alm_company.Company',
                                     related_name='users')

    class Meta:
        verbose_name = _('user')
        db_table = settings.DB_PREFIX.format('user')

    objects = UserManager()

    def is_authenticated(self):
        return True

    def get_username(self):
        return "%s %s" % (self.first_name, self.last_name)

    def say_hi(self):
        return 'hi'

    def get_company(self):
        return self.company.first()

    def get_owned_company(self):
        return self.owned_company.first()

    def get_subscriptions(self):
        return self.subscriptions.all()

    def get_active_subscriptions(self):
        return self.subscriptions.filter(is_active=True)

    def connected_products(self):
        rv = []
        for s in self.get_active_subscriptions():
            rv.append(s.product)
        return rv

    def is_product_connected(self, product):
        return product in self.connected_products()

    def connect_product(self, product):
        from almanet.models import Subscription
        try:
            s = Subscription.objects.get(product=product, user=self)
        except Subscription.DoesNotExist:
            s = Subscription(product=product, user=self)
        else:
            s.is_active = True
        s.save()


    def disconnect_product(self, product):
        s = self.subscriptions.filter(is_active=True, product=product).first()
        if s:
            s.is_active = False
            s.save()
