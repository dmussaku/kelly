from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class User(AbstractBaseUser):

    #REQUIRED_FIELDS = ['email']
    first_name = models.CharField(_('first name'), max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    email = models.EmailField(_('email address'), unique=True, blank=False)
    is_active = models.BooleanField(_('active'), default=True)
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        db_table = settings.DB_PREFIX.format('user')

    objects = UserManager()

    def is_authenticated(self):
        return True

    def get_username(self):
        return "%s %s" % (self.first_name, self.last_name)
