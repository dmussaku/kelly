from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from alm_vcard.models import *


class VCardResource(ModelResource):
    """
    GET Method 
    I{URL}:  U{alma.net:8000/api/v1/vcard/}
    
    Description
    Api for VCard model 
    """
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


class VCardGeoResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Geo.objects.all()
        resource_name = 'vcard_geo'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardAdrResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Adr.objects.all()
        resource_name = 'vcard_adr'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardAgentResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Agent.objects.all()
        resource_name = 'vcard_agent'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardCategoryResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Category.objects.all()
        resource_name = 'vcard_category'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardKeyResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Key.objects.all()
        resource_name = 'vcard_key'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardLabelResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Label.objects.all()
        resource_name = 'vcard_label'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardMailerResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Mailer.objects.all()
        resource_name = 'vcard_mailer'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardNicknameResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Nickname.objects.all()
        resource_name = 'vcard_nickname'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardNoteResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Note.objects.all()
        resource_name = 'vcard_note'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardRoleResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Role.objects.all()
        resource_name = 'vcard_role'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardTitleResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Title.objects.all()
        resource_name = 'vcard_title'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardTzResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Tz.objects.all()
        resource_name = 'vcard_tz'
        authentication = SessionAuthentication()
        authorization = Authorization()


class VCardUrlResource(ModelResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta:
        queryset = Url.objects.all()
        resource_name = 'vcard_url'
        authentication = SessionAuthentication()
        authorization = Authorization()
