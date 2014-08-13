from django.db import models
from django.utils.translation import ugettext_lazy as _
from django import forms

from .widgets import AddressMultiWidget


class AddressField(models.Field):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        from alm_contact.models import Address
        if value in (None,''):
            return Address()
        if isinstance(value, Address):
            return value

        fields = value.split('#')
        if len(fields) != 7:
            raise forms.ValidationError("Invalid input for a Address instance")
        address = Address(
            box = fields[0],
            extended = fields[1],
            code = fields[2],
            street = fields[3],
            city = fields[4],
            region = fields[5],
            country = fields[6]
        )
        return address

    def get_prep_value(self, value):
        from alm_contact.models import Address
        if value and isinstance(value, Address):
            return '%s#%s#%s#%s#%s#%s#%s' % (value.box, value.extended, value.code, value.street, value.city, value.region, value.country)
        return value

    def get_internal_type(self):
        return 'CharField'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': AddressFormField}
        defaults.update(kwargs)
        return super(AddressField, self).formfield(**defaults)

class AddressFormField(forms.MultiValueField):
    widget = AddressMultiWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
        )
        super(AddressFormField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return '#'.join(data_list)
        return ''

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^alm_contact\.fields\.AddressField"])