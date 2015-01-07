from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from alm_vcard.models import *

def vcard_rel_dehydrate(bundle):
    if bundle.data.get('vcard'):
        bundle.data['vcard'] = bundle.obj.vcard.id
    return bundle

class BaseVCardResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication())
        authorization = Authorization()

    # def full_dehydrate(self, bundle, for_list=False):
    #     bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
    #     return bundle

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
                              related_name='vcard', null=True, full=True)
    orgs = fields.ToManyField('alm_vcard.api.VCardOrgResource', 'org_set',
                              related_name='vcard', null=True, full=True)
    geos = fields.ToManyField('alm_vcard.api.VCardGeo', 'geo_set',
                              related_name='vcard', null=True, full=True)
    adrs = fields.ToManyField('alm_vcard.api.VCardAdrResource', 'adr_set',
                              related_name='vcard', null=True, full=True)
    agents = fields.ToManyField('alm_vcard.api.VCardAgentResource', 'agent_set',
                              related_name='vcard', null=True, full=True)
    categories = fields.ToManyField('alm_vcard.api.VCardCategoryResource', 'category_set',
                              related_name='vcard', null=True, full=True)
    keys = fields.ToManyField('alm_vcard.api.VCardKeyResource', 'key_set',
                              related_name='vcard', null=True, full=True)
    labels = fields.ToManyField('alm_vcard.api.VCardLabelResource', 'label_set',
                              related_name='vcard', null=True, full=True)
    mailers = fields.ToManyField('alm_vcard.api.VCardMailerResource', 'mailer_set',
                              related_name='vcard', null=True, full=True)
    nicknames = fields.ToManyField('alm_vcard.api.VCardNicknameResource', 'nickname_set',
                              related_name='vcard', null=True, full=True)
    notes = fields.ToManyField('alm_vcard.api.VCardNoteResource', 'note_set',
                              related_name='vcard', null=True, full=True)
    roles = fields.ToManyField('alm_vcard.api.VCardRoleResource', 'role_set',
                              related_name='vcard', null=True, full=True)
    titles = fields.ToManyField('alm_vcard.api.VCardTitleResource', 'title_set',
                              related_name='vcard', null=True, full=True)
    tzs = fields.ToManyField('alm_vcard.api.VCardTzResource', 'tz_set',
                              related_name='vcard', null=True, full=True)
    urls = fields.ToManyField('alm_vcard.api.VCardUrlResource', 'url_set',
                              related_name='vcard', null=True, full=True)

    class Meta(BaseVCardResource.Meta):
        queryset = VCard.objects.all()
        resource_name = 'vcard'

    def obj_delete(self, bundle, **kwargs):
        print "i was here"
        return super(self.__class__, self).obj_delete(bundle, **kwargs)

class VCardEmailResource(BaseVCardResource):
    vcard = fields.ForeignKey(VCardResource, 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Email.objects.all()
        resource_name = 'vcard_email'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle

    # def full_dehydrate(self, bundle, for_list=True):
    #     bundle = super(self.__class__, self).full_dehydrate(bundle)
    #     bundle = vcard_rel_dehydrate(bundle)
    #     return bundle

class VCardTelResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Tel.objects.all()
        resource_name = 'vcard_tel'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardOrgResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Org.objects.all()
        resource_name = 'vcard_org'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardGeoResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Geo.objects.all()
        resource_name = 'vcard_geo'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardAdrResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Adr.objects.all()
        resource_name = 'vcard_adr'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardAgentResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Agent.objects.all()
        resource_name = 'vcard_agent'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardCategoryResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Category.objects.all()
        resource_name = 'vcard_category'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardKeyResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Key.objects.all()
        resource_name = 'vcard_key'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardLabelResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Label.objects.all()
        resource_name = 'vcard_label'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardMailerResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Mailer.objects.all()
        resource_name = 'vcard_mailer'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardNicknameResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Nickname.objects.all()
        resource_name = 'vcard_nickname'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardNoteResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Note.objects.all()
        resource_name = 'vcard_note'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardRoleResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Role.objects.all()
        resource_name = 'vcard_role'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardTitleResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Title.objects.all()
        resource_name = 'vcard_title'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardTzResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Tz.objects.all()
        resource_name = 'vcard_tz'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle


class VCardUrlResource(BaseVCardResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(BaseVCardResource.Meta):
        queryset = Url.objects.all()
        resource_name = 'vcard_url'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle)
        bundle = vcard_rel_dehydrate(bundle)
        return bundle
