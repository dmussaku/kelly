from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from alm_vcard.models import VCard, Email, Tel, Org
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization

class VCardResource(ModelResource):
	emails = fields.ToManyField('alm_vcard.api.EmailResource', 'email_set', related_name='vcard', null=True, full=True)
	tels = fields.ToManyField('alm_vcard.api.TelResource', 'tel_set',related_name='vcard', null=True, full=True)
	orgs = fields.ToManyField('alm_vcard.api.OrgResource', 'org_set',related_name='vcard', null=True, full=True)
	
	class Meta:
		queryset = VCard.objects.all()
		resource_name = 'vcard'
		authentication = BasicAuthentication()
		authorization = Authorization()

	def obj_create(self, bundle, **kw):
		bundle = super(VCardResource, self).obj_create(bundle, **kw)
		return bundle

	def obj_update(self, bundle, **kw):
		bundle = super(VCardResource, self).obj_update(bundle, **kw)
		return bundle

	def obj_delete(self, bundle, **kw):
		bundle = super(VCardResource, self).obj_delete(bundle, **kw)
		return bundle


class EmailResource(ModelResource):
	vcard = fields.ForeignKey(VCardResource, 'vcard')

	class Meta:
		queryset = Email.objects.all()
		resource_name = 'email'
		authentication = BasicAuthentication()
		authorization = Authorization()


class TelResource(ModelResource):
	vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

	class Meta:
		queryset = Tel.objects.all()
		resource_name = 'tel'
		authentication = BasicAuthentication()
		authorization = Authorization()



class OrgResource(ModelResource):
	vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

	class Meta:
		queryset = Org.objects.all()
		resource_name = 'org'
		authentication = BasicAuthentication()
		authorization = Authorization()



