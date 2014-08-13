from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import vobject

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
                                                        box='12',
                                                        extended='222',
                                                        code='6000', 
                                                        country='Kazakhstan', 
                                                        city='Almaty', 
                                                        street='Dostyk', 
                                                        region='Almalinskii')
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