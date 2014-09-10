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
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('user')
        db_table = settings.DB_PREFIX.format('user')

    objects = UserManager()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def is_authenticated(self):
        return True

    def has_module_perms(self, module):
        if self.is_admin:
            return True
        return False

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def get_short_name(self):
        return self.first_name

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

    def connected_services(self):
        rv = []
        for s in self.get_active_subscriptions():
            rv.append(s.service)
        return rv

    def is_service_connected(self, service):
        return service in self.connected_services()

    def connect_service(self, service):
        from almanet.models import Subscription
        try:
            s = Subscription.objects.get(service=service, user=self)
        except Subscription.DoesNotExist:
            s = Subscription(service=service, user=self)
        else:
            s.is_active = True
        s.save()

    def disconnect_service(self, service):
        s = self.subscriptions.filter(is_active=True, service=service).first()
        if s:
            s.is_active = False
            s.save()
