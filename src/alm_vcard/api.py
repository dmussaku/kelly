from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from alm_vcard.models import *
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from tastypie.exceptions import NotFound
from collections import OrderedDict

def vcard_rel_dehydrate(bundle):
    if bundle.data.get('vcard'):
        bundle.data['vcard'] = bundle.obj.vcard.id
    return bundle


class CommonMeta:
    list_allowed_methods = ['get', 'post']
    detail_allowed_methods = ['get', 'post', 'put', 'delete']
    authentication = MultiAuthentication(BasicAuthentication(),
                                         SessionAuthentication())
    authorization = Authorization()
    include_resource_uri = False


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
    # orgs = fields.ToManyField('alm_vcard.api.VCardOrgResource', 'org_set',
    #                           related_name='vcard', null=True, full=True)
    # geos = fields.ToManyField('alm_vcard.api.VCardGeoResource', 'geo_set',
    #                           related_name='vcard', null=True, full=True)
    adrs = fields.ToManyField('alm_vcard.api.VCardAdrResource', 'adr_set',
                              related_name='vcard', null=True, full=True)
    # agents = fields.ToManyField('alm_vcard.api.VCardAgentResource', 'agent_set',
    #                           related_name='vcard', null=True, full=True)
    categories = fields.ToManyField('alm_vcard.api.VCardCategoryResource', 'category_set',
                              related_name='vcard', null=True, full=True)
    # keys = fields.ToManyField('alm_vcard.api.VCardKeyResource', 'key_set',
    #                           related_name='vcard', null=True, full=True)
    # labels = fields.ToManyField('alm_vcard.api.VCardLabelResource', 'label_set',
    #                           related_name='vcard', null=True, full=True)
    # mailers = fields.ToManyField('alm_vcard.api.VCardMailerResource', 'mailer_set',
    #                           related_name='vcard', null=True, full=True)
    # nicknames = fields.ToManyField('alm_vcard.api.VCardNicknameResource', 'nickname_set',
    #                           related_name='vcard', null=True, full=True)
    notes = fields.ToManyField('alm_vcard.api.VCardNoteResource', 'note_set',
                              related_name='vcard', null=True, full=True)
    # roles = fields.ToManyField('alm_vcard.api.VCardRoleResource', 'role_set',
    #                           related_name='vcard', null=True, full=True)
    titles = fields.ToManyField('alm_vcard.api.VCardTitleResource', 'title_set',
                              related_name='vcard', null=True, full=True)
    # tzs = fields.ToManyField('alm_vcard.api.VCardTzResource', 'tz_set',
    #                           related_name='vcard', null=True, full=True)
    urls = fields.ToManyField('alm_vcard.api.VCardUrlResource', 'url_set',
                              related_name='vcard', null=True, full=True)

    class Meta(CommonMeta):
        queryset = VCard.objects.all().prefetch_related('email_set', 'tel_set', 'org_set', 'adr_set', 'category_set', 'title_set', 'url_set')
        excludes = ['id','resource_uri']
        resource_name = 'vcard'

    # def full_dehydrate(self, bundle, for_list=False):
    #     bundle = super(self.__class__, self).full_dehydrate(bundle)
    #     del bundle.data['resource_uri']
    #     return bundle


    @transaction.atomic()
    def obj_create(self, bundle, **kwargs):
        if bundle.data.get('categories'):
            categories = [x['data'] for x in bundle.data['categories']]
            bundle.data['categories'] = [{"data":x} for x in list(OrderedDict.fromkeys(categories))]
        if kwargs.get('pk'):
            bundle.obj = VCard.objects.get(contact=int(kwargs['pk']))
            print bundle.obj
            print bundle.obj.id
            bundle.obj.delete()
        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        return self.save(bundle)
        # return super(self.__class__, self).obj_create(bundle, **kwargs)

    @transaction.atomic()
    def full_hydrate(self, bundle):
        return super(self.__class__, self).full_hydrate(bundle)

    def obj_delete(self, bundle, **kwargs):
        return super(self.__class__, self).obj_delete(bundle, **kwargs)


class VCardRelatedResource(ModelResource):
    vcard = fields.ForeignKey(VCardResource, 'vcard')

    def hydrate_vcard(self, bundle):
        vcard_id = bundle.data.get('vcard',"")
        if (vcard_id and type(vcard_id)==int):
            bundle.obj.vcard = VCard.objects.get(id=vcard_id)
        return bundle

    # def dehydrate_vcard(self, bundle):
    #     return bundle.obj.vcard_id


class VCardEmailResource(VCardRelatedResource):
    vcard = fields.ForeignKey(VCardResource, 'vcard')

    class Meta(CommonMeta):
        queryset = Email.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_email'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardTelResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Tel.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_tel'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardGeoResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Geo.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_geo'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardAdrResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Adr.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_adr'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardAgentResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Agent.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_agent'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardCategoryResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Category.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_category'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardKeyResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Key.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_key'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardLabelResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Label.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_label'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardMailerResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Mailer.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_mailer'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardNicknameResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Nickname.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_nickname'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardNoteResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Note.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_note'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardRoleResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Role.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_role'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardTitleResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Title.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_title'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardTzResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Tz.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_tz'

    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle


class VCardUrlResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Url.objects.all()
        excludes = ['id', 'vcard', 'resource_uri']
        resource_name = 'vcard_url'


    def full_dehydrate(self, bundle, for_list=True):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        del bundle.data['vcard']
        return bundle
