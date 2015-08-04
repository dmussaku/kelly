from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime
from alm_user.models import User
import re


class Company(models.Model):
    name = models.CharField(max_length=100, blank=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)
    subdomain = models.CharField(_('subdomain'), max_length=300,
                                 blank=False, unique=True)

    class Meta:
        verbose_name = _('company')
        db_table = settings.DB_PREFIX.format('company')

    def __unicode__(self):
        return u'%s' % self.name

    @classmethod
    def generate_subdomain(self, subdomain):
        sd = re.sub('[\W]', '', subdomain).lower()
        if sd in settings.BUSY_SUBDOMAINS:
            sd += str(1)
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

    def get_users(self):
        return User.objects.filter(id__in=[a.id for a in self.accounts.all()])

    @classmethod
    def verify_company_by_subdomain(cls, company, subdomain):
        lco = company
        try:
            rco = cls.objects.get(subdomain=subdomain)
        except cls.DoesNotExist:
            rco = None
        if rco is None:
            return False
        return lco.pk == rco.pk

    @classmethod
    def build_company(cls, name):
        subdomain = Company.generate_subdomain(name)
        company = Company(name=name, subdomain=subdomain)
        company.save()
        return company
