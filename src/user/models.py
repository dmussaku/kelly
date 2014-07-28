from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager as contrib_user_manager
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

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

    USERNAME_FIELD = 'email'

    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(_('active'), default=True)

    city = models.CharField(_('city'), max_length=30)
    country = models.CharField(_('country'), max_length=30, choices=settings.COUNTRIES)

    class Meta:
        verbose_name = _('user')
        db_table = settings.DB_PREFIX.format('user')

    objects = UserManager()
