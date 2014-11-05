from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from alm_vcard.models import VCard, Email, Tel, Org
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization


class VCardResource(ModelResource):
    emails = fields.ToManyField('alm_vcard.api.VCardEmailResource',
                                'email_set', related_name='vcard', null=True,
                                full=True)
    tels = fields.ToManyField('alm_vcard.api.VCardTelResource', 'tel_set',
                              related_name='vcard', null=True, full=True)
    orgs = fields.ToManyField('alm_vcard.api.VCardOrgResource', 'org_set',
                              related_name='vcard', null=True, full=True)

    class Meta:
        queryset = VCard.objects.all()
        resource_name = 'vcard'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardEmailResource(ModelResource):
    vcard = fields.ForeignKey(VCardResource, 'vcard')

    class Meta:
        queryset = Email.objects.all()
        resource_name = 'vcard_email'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardTelResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Tel.objects.all()
        resource_name = 'vcard_tel'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardOrgResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Org.objects.all()
        resource_name = 'vcard_org'
        authentication = SessionAuthentication()
        authorization = Authorization()
