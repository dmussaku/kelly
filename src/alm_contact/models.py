from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
import vobject

from almanet import settings

from .fields import AddressField

STATUSES = (_('new_contact'), _('lead_contact'), _('opportunity_contact'), _('client_contact') )
STATUS_NAMES = (NEW, LEAD, OPPORTUNITY, CLIENT) = range(len(STATUSES))

#Contact model: (first_name, last_name, company_name, phone, email)
class Contact(models.Model):
    STATUS_CODES = dict(zip(STATUS_NAMES, STATUSES))

    first_name = models.CharField(_('first name'), max_length=31,
                                  null=False, blank=False)
    middle_name = models.CharField(_('middle name'), max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    company_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    email = models.EmailField(unique=True, blank=False)
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    job_address = AddressField(_('job address'), max_length=200, blank=True)
    status = models.IntegerField(_('contact status'), max_length=30, choices=enumerate(STATUSES), default=NEW)

    class Meta:
        verbose_name = _('contact')
        db_table = settings.DB_PREFIX.format('contact')

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

    def save(self, **kwargs):
        if (not self.date_created):
            self.date_created = timezone.now()
        super(Contact, self).save(**kwargs)

    def is_new(self):
        return self.status == NEW

    def is_lead(self):
        return self.status == LEAD

    def is_opportunity(self):
        return self.status == OPPORTUNITY

    def is_client(self):
        return self.status == CLIENT


class Address(object):
    """
        Class for representing complex address model,
        do not have its own db table, stored as serialized string in Contact model's AddressField
    """

    def __init__(self, box = None, extended = None, code = None, street = None, city = None, region = None, country = None):
        self.box = box
        self.extended = extended
        self.code = code
        self.street = street
        self.city = city
        self.region = region
        self.country = country

    def __unicode__():
        return self.country