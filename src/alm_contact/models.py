from django.db import models
#Contact model: (first_name, last_name, company_name, phone, email)
class Contact(models.Model):
	first_name = models.CharField(_('first name'), max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    company_name = models.CharField(_('company name'), max_length=50, blank=True)
    phone = models.CharField(_('phone'), max_length=12, blank=True)
    email = models.EmailField(_('email address'), unique=True, blank=False)

    class Meta:
        verbose_name = _('contact')
        db_table = settings.DB_PREFIX.format('contact')