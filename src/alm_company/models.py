from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import re


class Company(models.Model):
    name = models.CharField(max_length=100, blank=False)
    owner = models.ManyToManyField('alm_user.User', related_name='owned_company')
    subdomain = models.CharField(_('subdomain'), max_length=300, blank=False, unique=True)

    class Meta:
        verbose_name = _('company')
        db_table = settings.DB_PREFIX.format('company')

    @classmethod
    def generate_subdomain(self, subdomain):
        sd = re.sub('[\W]', '', subdomain).lower()
        i = 1
        test_sd = sd
        while(True):
            try:
                Company.objects.get(subdomain=test_sd)
            except Company.DoesNotExist:
                break
            else:
                test_sd = sd + str(i)
                i += 1
        return test_sd

    def get_owner(self):
        o = self.owner.all()
        if len(o > 0):
            return o[0]
        return None

    def get_users(self):
        us = self.users.all()
        if len(us > 0):
            return us
        return None
