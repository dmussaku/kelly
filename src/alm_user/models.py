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

    #REQUIRED_FIELDS = ['email']
    first_name = models.CharField(_('first name'), max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    email = models.EmailField(_('email address'), unique=True, blank=False)
    is_active = models.BooleanField(_('active'), default=True)
    USERNAME_FIELD = 'email'

    city = models.CharField(_('city'), max_length=30)
    country = models.CharField(_('country'), max_length=30, choices=settings.COUNTRIES)

    company = models.ManyToManyField('alm_company.Company', related_name='users')

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
        co = self.company.all()
        if len(co) > 0:
            return co[0]
        return None

    def get_owned_company(self):
        oco = self.owned_company.all()
        if len(oco) > 0:
            return oco[0]
        return None

