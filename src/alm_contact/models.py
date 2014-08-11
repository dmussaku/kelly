from django.db import models
from almanet import settings
#Contact model: (first_name, last_name, company_name, phone, email)
class Contact(models.Model):
    first_name = models.CharField(max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    company_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    email = models.EmailField(unique=True, blank=False)

    class Meta:
        verbose_name = 'contact'
        db_table = settings.DB_PREFIX.format('contact')