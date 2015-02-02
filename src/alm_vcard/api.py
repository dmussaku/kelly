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

    class Meta(CommonMeta):
        queryset = VCard.objects.all()
        resource_name = 'vcard'

    @transaction.commit_on_success()
    def obj_create(self, bundle, **kwargs):
        return super(self.__class__, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        if not bundle.obj or not self.get_bundle_detail_data(bundle):
            try:
                lookup_kwargs = self.lookup_kwargs_with_identifiers(bundle, kwargs)
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs
            try:
                # bundle.obj = self.obj_get(bundle=bundle, **lookup_kwargs)
                # bundle.obj.delete()
                bundle.obj = VCard.objects.get(contact=int(kwargs['pk']))
                bundle.obj.delete()
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")
        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        # with transaction.atomic():  
        #     bundle = self.full_hydrate(bundle)
        return self.save(bundle, skip_errors=skip_errors)

    @transaction.commit_on_success()
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

    def dehydrate_vcard(self, bundle):
        return bundle.obj.vcard_id


class VCardEmailResource(VCardRelatedResource):
    vcard = fields.ForeignKey(VCardResource, 'vcard')

    class Meta(CommonMeta):
        queryset = Email.objects.all()
        resource_name = 'vcard_email'


class VCardTelResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Tel.objects.all()
        resource_name = 'vcard_tel'


class VCardOrgResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Org.objects.all()
        resource_name = 'vcard_org'


class VCardGeoResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Geo.objects.all()
        resource_name = 'vcard_geo'


class VCardAdrResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Adr.objects.all()
        resource_name = 'vcard_adr'


class VCardAgentResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Agent.objects.all()
        resource_name = 'vcard_agent'


class VCardCategoryResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Category.objects.all()
        resource_name = 'vcard_category'


class VCardKeyResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Key.objects.all()
        resource_name = 'vcard_key'


class VCardLabelResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Label.objects.all()
        resource_name = 'vcard_label'


class VCardMailerResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Mailer.objects.all()
        resource_name = 'vcard_mailer'


class VCardNicknameResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Nickname.objects.all()
        resource_name = 'vcard_nickname'


class VCardNoteResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Note.objects.all()
        resource_name = 'vcard_note'


class VCardRoleResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Role.objects.all()
        resource_name = 'vcard_role'


class VCardTitleResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Title.objects.all()
        resource_name = 'vcard_title'


class VCardTzResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Tz.objects.all()
        resource_name = 'vcard_tz'


class VCardUrlResource(VCardRelatedResource):
    vcard = fields.ForeignKey('alm_vcard.api.VCardResource', 'vcard')

    class Meta(CommonMeta):
        queryset = Url.objects.all()
        resource_name = 'vcard_url'
