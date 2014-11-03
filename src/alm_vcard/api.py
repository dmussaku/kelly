from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from alm_vcard.models import VCard, Email
from tastypie import fields

class EmailResource(ModelResource):
	vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

	class Meta:
		queryset = Email.objects.all()
		resource_name = 'email'

class VCardResource(ModelResource):
	emails = fields.ToManyField(EmailResource, 'email_set', null=True, full=True)
	class Meta:
		queryset = VCard.objects.all()
		resource_name = 'vcard'
		filtering={'email':ALL_WITH_RELATIONS}

