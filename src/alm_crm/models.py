from django.db import models
from django.utils import timezone
from almanet import settings
from alm_company.models import Company
from alm_user.models import User
from almanet.models import Product


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

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

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
        verbose_name = 'value'
        db_table = settings.DB_PREFIX.format('value')

    def __unicode__(self):
        return "%s %s %s" % (self.amount, self.currency, self.salary)


class Goal(models.Model):
    STATUS_OPTIONS = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('N', 'New'),
        )
    product = models.OneToOneField(Product, related_name='goal_product') 
    assignee = models.ForeignKey(User, related_name='goal_assignee')
    followers = models.ManyToManyField(User, related_name='goal_followers')
    contact = models.OneToOneField(Contact) 
    project_value = models.OneToOneField(Value, related_name='goal_project_value')
    real_value = models.OneToOneField(Value, related_name = 'goal_real_value')
    name = models.CharField(max_length=30, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_OPTIONS, default='N')
    date_created = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        verbose_name = 'goal'
        db_table = settings.DB_PREFIX.format('goal')