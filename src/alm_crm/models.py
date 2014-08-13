from django.db import models
from django.utils import timezone
from almanet import settings

class Contact(models.Model):
    first_name = models.CharField(max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    company_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    email = models.EmailField(unique=True, blank=False)
    date_created = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        verbose_name = 'contact'
        db_table = settings.DB_PREFIX.format('contact')

    def save(self, **kwargs):
        if (not self.date_created):
            self.date_created = timezone.now()
        super(Contact, self).save(**kwargs)

class Value(models.Model):
	SALARY_OPTIONS = (
		('monthly', 'Monthly'),
		('annualy', 'Annualy'),
		('instant', 'Instant'),
		)
	CURRENCY_OPTIONS = (
		('USD', 'US Dollar'),
		('RUB', 'Rubbles'),
		('KZT', 'Tenge'),
		)
	salary = models.CharField(max_length=7, choices=SALARY_OPTIONS, default='instant')
	amount = models.IntegerField()
	currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS, default='KZT')

	class Meta:
        verbose_name = _('value')
        db_table = settings.DB_PREFIX.format('value')