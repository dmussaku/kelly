from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from alm_vcard.models import *

class BaseVCardResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication())
        authorization = Authorization()

class VCardResource(BaseVCardResource):
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
                              related_name='vcard', null=True, full=False)
    orgs = fields.ToManyField('alm_vcard.api.VCardOrgResource', 'org_set',
                              related_name='vcard', null=True, full=False)


    class Meta(BaseVCardResource.Meta):
        queryset = VCard.objects.all()
        resource_name = 'vcard'


class VCardEmailResource(BaseVCardResource):
    vcard = fields.ForeignKey(VCardResource, 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Email.objects.all()
        resource_name = 'vcard_email'


class VCardTelResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Tel.objects.all()
        resource_name = 'vcard_tel'


class VCardOrgResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Org.objects.all()
        resource_name = 'vcard_org'


class VCardGeoResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Geo.objects.all()
        resource_name = 'vcard_geo'


class VCardAdrResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Adr.objects.all()
        resource_name = 'vcard_adr'


class VCardAgentResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Agent.objects.all()
        resource_name = 'vcard_agent'


class VCardCategoryResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Category.objects.all()
        resource_name = 'vcard_category'


class VCardKeyResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Key.objects.all()
        resource_name = 'vcard_key'


class VCardLabelResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Label.objects.all()
        resource_name = 'vcard_label'


class VCardMailerResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Mailer.objects.all()
        resource_name = 'vcard_mailer'


class VCardNicknameResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Nickname.objects.all()
        resource_name = 'vcard_nickname'


class VCardNoteResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Note.objects.all()
        resource_name = 'vcard_note'


class VCardRoleResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Role.objects.all()
        resource_name = 'vcard_role'


class VCardTitleResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Title.objects.all()
        resource_name = 'vcard_title'


class VCardTzResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Tz.objects.all()
        resource_name = 'vcard_tz'


class VCardUrlResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Url.objects.all()
        resource_name = 'vcard_url'
