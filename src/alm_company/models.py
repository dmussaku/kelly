from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import re
from almanet.settings import BUSY_SUBDOMAINS


class Company(models.Model):
    name = models.CharField(max_length=100, blank=False)
    owner = models.ManyToManyField('alm_user.User',
                                   related_name='owned_company')
    subdomain = models.CharField(_('subdomain'), max_length=300,
                                 blank=False, unique=True)

    class Meta:
        verbose_name = _('company')
        db_table = settings.DB_PREFIX.format('company')

    @classmethod
    def generate_subdomain(self, subdomain):
        sd = re.sub('[\W]', '', subdomain).lower()
        if sd in BUSY_SUBDOMAINS:
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

    def get_owner(self):
        return self.owner.first()

    def get_users(self):
        return self.users.all()

    def get_connected_services(self):
        return self.subscriptions.filter(is_active=True)

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
