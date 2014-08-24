from django.db import models
from django.utils.translation import ugettext_lazy as _
from almanet import settings
from alm_user.models import User
from almanet.models import Product
from django.template.loader import render_to_string

# import vcard as django_vcard


STATUSES_CAPS = (
    _('new_contact'),
    _('lead_contact'),
    _('opportunity_contact'),
    _('client_contact'))
STATUSES = (NEW, LEAD, OPPORTUNITY, CLIENT) = range(len(STATUSES_CAPS))


class Contact(models.Model):

    STATUS_CODES = zip(STATUSES, STATUSES_CAPS)
    TYPES = (COMPANY_TP, USER_TP) = ('co', 'user')
    TYPES_WITH_CAPS = zip((COMPANY_TP, _('company type')),
                          (USER_TP, _('user type')))
    status = models.IntegerField(
        _('contact status'),
        max_length=30,
        choices=STATUS_CODES, default=NEW)
    tp = models.CharField(
        _('contact type'),
        max_length=30,
        choices=TYPES_WITH_CAPS, default=USER_TP)
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    vcard = models.ForeignKey('alm_vcard.VCard', blank=True, null=True)
    company_contact = models.ForeignKey(
        'Contact', blank=True, null=True, related_name='user_contacts')
    # first_name = models.CharField(max_length=31,
    #                               null=False, blank=False)
    # last_name = models.CharField(max_length=30, blank=False)
    # company_name = models.CharField(max_length=50, blank=True)
    # phone = models.CharField(max_length=12, blank=True)
    # email = models.EmailField(unique=True, blank=False)

    # job_address = AddressField(_('job address'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('contact')
        db_table = settings.DB_PREFIX.format('contact')

    def __unicode__(self):
        return "%s %s" % (self.vcard, self.tp)

    @property
    def name(self):
        if not self.vcard:
            return 'Unknown'
        return self.vcard.fn

    def get_tp(self):
        return dict(self.TYPES_WITH_CAPS).get(self.tp, None)

    def is_new(self):
        return self.status == NEW

    def is_lead(self):
        return self.status == LEAD

    def is_opportunity(self):
        return self.status == OPPORTUNITY

    def is_client(self):
        return self.status == CLIENT

    def export_to(self, tp, **options):
        if not tp in ('html', 'vcard'):
            return False
        exporter = getattr(self, 'to_{}'.format(tp))
        return exporter(**options)

    def to_vcard(self, locale='ru_RU'):
        return self.vcard.exportTo('vCard')

    def to_html(self, locale='ru_RU'):
        tpl_name = 'vcard/_detail.%s.html' % locale
        context = {'object': self.vcard}
        return render_to_string(tpl_name, context)


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
    salary = models.CharField(
        max_length=7,
        choices=SALARY_OPTIONS,
        default='instant')
    amount = models.IntegerField()
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_OPTIONS,
        default='KZT')

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
    project_value = models.OneToOneField(
        Value, related_name='goal_project_value')
    real_value = models.OneToOneField(
        Value, related_name='goal_real_value')
    name = models.CharField(max_length=30, blank=False)
    status = models.CharField(
        max_length=2, choices=STATUS_OPTIONS, default='N')
    date_created = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        verbose_name = 'goal'
        db_table = settings.DB_PREFIX.format('goal')


# class Address(object):
#     """
#         Class for representing complex address model,
#         do not have its own db table,
#         stored as serialized string in Contact model's AddressField
#     """

#     def __init__(self, box = None, extended = None, code = None, street = None, city = None, region = None, country = None):
#         self.box = box
#         self.extended = extended
#         self.code = code
#         self.street = street
#         self.city = city
#         self.region = region
#         self.country = country

#     def __unicode__(self):
#         return self.country
