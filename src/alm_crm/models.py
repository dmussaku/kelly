from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from almanet import settings
from alm_company.models import Company
from alm_user.models import User
from almanet.models import Product
from django.db.models import signals
from django.dispatch import receiver
import vobject
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from almanet import settings

from .fields import AddressField

STATUSES = (_('new_contact'), _('lead_contact'), _('opportunity_contact'), _('client_contact') )
STATUS_NAMES = (NEW, LEAD, OPPORTUNITY, CLIENT) = range(len(STATUSES))


class Contact(models.Model):

    STATUS_CODES = dict(zip(STATUS_NAMES, STATUSES))
    first_name = models.CharField(max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    company_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    email = models.EmailField(unique=True, blank=False)
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    job_address = AddressField(_('job address'), max_length=200, blank=True)
    status = models.IntegerField(_('contact status'), max_length=30, choices=enumerate(STATUSES), default=NEW)
    latest_activity = models.OneToOneField('Activity', related_name ='contact_latest_activity', null=True)
    mentions = generic.GenericRelation('Mention')

    class Meta:
        verbose_name = _('contact')
        db_table = settings.DB_PREFIX.format('contact')

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def to_vcard(self):

        VCARD_MAPPING = {
            'fn':       { 'type': None, 'value': "%s %s" % (self.first_name, self.last_name) }, 
            'n' :       { 'type': None, 'value': vobject.vcard.Name(
                                                        family=self.last_name,
                                                        given=self.first_name, 
                                                        additional='', 
                                                        prefix='', 
                                                        suffix='' )
                        },
            'tel':      [{ 'type': 'CELL', 'value': self.phone }, { 'type': 'HOME', 'value': '+77272348956' }],
            'email':    { 'type': 'INTERNET', 'value': self.email },
            'org':      { 'type': None, 'value': 'Apple' },
            'adr':      [{ 'type': 'WORK', 'value': vobject.vcard.Address(
                                                        box=self.job_address.box,
                                                        extended=self.job_address.extended,
                                                        code=self.job_address.code, 
                                                        country=self.job_address.country, 
                                                        city=self.job_address.city, 
                                                        street=self.job_address.street, 
                                                        region=self.job_address.region)
                        }, { 'type': 'HOME', 'value': vobject.vcard.Address(
                                                        box='12',
                                                        extended='222',
                                                        code='6000', 
                                                        country='Kazakhstan', 
                                                        city='Almaty', 
                                                        street='Dostyk', 
                                                        region='Almalinskii')
                        }],
            'bday':     { 'type': None, 'value': "%s-%s-%s" % ('2012', '03', '30') },
            'url':      { 'type': None, 'value':'http://google.com' },
            'note':     { 'type': None, 'value':'test note' },
        }

        def add_attribute(vcard, attribute, desc):
            rv = vcard.add(attribute)
            if desc['type'] is not None:
                rv.type_param = desc['type']
            rv.value = desc['value']

        vcard = vobject.vCard()
        for attribute, desc in VCARD_MAPPING.iteritems():
            if isinstance(desc, list):
                for item in desc:
                    add_attribute(vcard, attribute, item)
            else:
                add_attribute(vcard, attribute, desc)
            
        return vcard

    def is_new(self):
        return self.status == NEW

    def is_lead(self):
        return self.status == LEAD

    def is_opportunity(self):
        return self.status == OPPORTUNITY

    def is_client(self):
        return self.status == CLIENT

    

    def get_latest_activity(self):
        return self.sales_cycles.aggregate(Max('contact_latest_activity'))

    def add_mention(self, user_ids=None):
        assert not user_ids is None and isinstance(user_ids, (list, set, tuple))
        self.mentions = [Mention.build_new(user_id, content_class=self.__class__, object_id=self.pk, save=True) for user_id in user_ids]
        self.save()


    @receiver(signals.post_save, sender='Activity')
    def set_latest_activity(sender, instance, created, **kwargs):
        if created:
            contact = instance.sales_cycle.contact
            contact.latest_activity = instance
            contact.save()


class Value(models.Model):
    #Type of payment
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


class SalesCycle(models.Model):
    STATUS_OPTIONS = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('N', 'New'),
        )
    products = models.ManyToManyField(Product, related_name='sales_cycle_product') 
    owner = models.ForeignKey(User, related_name='salescycle_owner')
    followers = models.ManyToManyField(User, related_name='sales_cycle_followers')
    contact = models.ForeignKey(Contact) 
    latest_activity = models.OneToOneField('Activity', related_name='latest_activity', null=True)
    project_value = models.OneToOneField(Value, related_name='sales_cycle_project_value')
    real_value = models.OneToOneField(Value, related_name = 'sales_cycle_real_value')
    #name = models.CharField(max_length=30, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_OPTIONS, default='N')
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    from_date = models.DateTimeField(blank=False, auto_now_add=True)
    to_date = models.DateTimeField(blank=False, auto_now_add=True)
    mentions = generic.GenericRelation('Mention')

    class Meta:
        verbose_name = 'sales_cycle'
        db_table = settings.DB_PREFIX.format('sales_cycle')

    def get_latest_activity(self):
        return self.activities.aggregate(Max('when'))

    def __unicode__(self):
        return '%s %s' % (self.contact, self.status )
    
    # Adds mentions to a current class, takes a lsit of user_ids as an input
    # and then runs through the list and calls the function build_new which
    # is declared in Mention class
    def add_mention(self, user_ids=None):
        assert not user_ids is None and isinstance(user_ids, (list, set, tuple))
        self.mentions = [Mention.build_new(user_id, content_class=self.__class__, object_id=self.pk, save=True) for user_id in user_ids]
        self.save()

    # @receiver(signals.post_save, sender='Activity')
    # def set_latest_activity(sender, instance, created, **kwargs):
    #     if created:
    #         instance.sales_cycle.latest_activity = instance

    # @receiver(signals.post_delete, sender='Activity')
    # def update_latest_activity(sender, instance, **kwargs):
    #     if instance.sales_cycle.latest_activity == instance:
    #         pass

class Address(object):
    '''
        Class for representing complex address model,
        do not have its own db table, stored as serialized string in Contact model's AddressField
    '''

    def __init__(self, box = None, extended = None, code = None, street = None, city = None, region = None, country = None):
        self.box = box
        self.extended = extended
        self.code = code
        self.street = street
        self.city = city
        self.region = region
        self.country = country

    class Meta:
        verbose_name = 'address'
        db_table = settings.DB_PREFIX.format('address')

    def __unicode__():
        return self.country

class Activity(models.Model):
    STATUS_OPTIONS = (
            ('W', 'waiting'),
            ('$', '1000'),
            ('1', 'Client is happy'),
            ('2', 'Client is OK'),
            ('3', 'Client is neutral'),
            ('4', 'Client is disappointed'),
            ('5', 'Client is angry')
        )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    when = models.DateTimeField(blank=True, auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_OPTIONS, default='')
    feedback = models.CharField(max_length=300)
    sales_cycle = models.ForeignKey(SalesCycle, related_name='activity_sales_cycle')
    author = models.ForeignKey(User, related_name='activity_author')

    class Meta:
        verbose_name = 'activity'
        db_table = settings.DB_PREFIX.format('activity')

    def __unicode__(self):
        return self.title


class Mention(models.Model):
    user_id = models.IntegerField()
    content_type = models.ForeignKey(ContentType)  
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s %s" % (self.user_id, self.content_object)

    @classmethod
    def build_new(cls, user_id, content_class=None, object_id=None, save=False):
        mention = cls(user_id=user_id)
        mention.content_type = ContentType.objects.get_for_model(content_class)
        mention.object_id = object_id
        if save:
            mention.save()
        return mention

class Comment(models.Model):
    comment = models.CharField(max_length=140)
    author = models.ForeignKey(User, related_name='comment_author')
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    date_edited = models.DateTimeField(blank=True)
    object_id = models.ForeignKey(User, related_name='object_id')
    content_type = models.CharField(max_length=1000)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    mentions = generic.GenericRelation('Mention')

    def __unicode__(self):
        return "%s's comment" % (self.author)

    def save(self, **kwargs):
        if self.date_created:
            self.date_edited = timezone.now()
            self.save()

    def add_mention(self, user_ids=None):
        assert not user_ids is None and isinstance(user_ids, (list, set, tuple))
        self.mentions = [Mention.build_new(user_id, content_class=self.__class__, object_id=self.pk, save=True) for user_id in user_ids]
        self.save()

    @classmethod
    def build_new(cls, user_id, content_class=None, object_id=None, save=False):
        comment = cls(user_id=user_id)
        comment.content_type = ContentType.objects.get_for_model(content_class)
        comment.object_id = object_id
        if save:
            comment.save()
        return comment