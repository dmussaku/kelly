#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .models import (
    SalesCycle,
    Milestone,
    Product,
    ProductGroup,
    Activity,
    Contact,
    ContactList,
    Share,
    Value,
    Comment,
    Mention,
    SalesCycleProductStat,
    SalesCycleLogEntry,
    Filter,
    HashTag,
    HashTagReference,
    CustomSection,
    CustomField,
    CustomFieldValue,
    ImportTask,
    ErrorCell
    )
from alm_user.models import User
from alm_user.api import UserResource
from alm_vcard.api import (
    VCardResource,
    VCardEmailResource,
    VCardTelResource,
    VCardOrgResource,
    VCardGeoResource,
    VCardAdrResource,
    VCardAgentResource,
    VCardCategoryResource,
    VCardKeyResource,
    VCardLabelResource,
    VCardMailerResource,
    VCardNicknameResource,
    VCardNoteResource,
    VCardRoleResource,
    VCardTitleResource,
    VCardTzResource,
    VCardUrlResource
    )
from alm_vcard.api import (
    VCardResource,
    VCardEmailResource,
    VCardTelResource,
    VCardOrgResource,
    VCardGeoResource,
    VCardAdrResource,
    VCardAgentResource,
    VCardCategoryResource,
    VCardKeyResource,
    VCardLabelResource,
    VCardMailerResource,
    VCardNicknameResource,
    VCardNoteResource,
    VCardRoleResource,
    VCardTitleResource,
    VCardTzResource,
    VCardUrlResource
    )
from alm_vcard.models import *
from almanet.settings import DEFAULT_SERVICE
from almanet.settings import TIME_ZONE
from almanet.utils.api import RequestContext, SessionAuthentication
from almanet.utils.env import get_subscr_id
from almanet.utils.ds import StreamList
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models,transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.utils import translation
from tastypie import fields, http
from tastypie.authentication import (
    MultiAuthentication,
    )
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.exceptions import ImmediateHttpResponse, NotFound, Unauthorized
from tastypie.resources import Resource, ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from django.db.models.loading import get_model
import ast
from datetime import datetime, timedelta
import pytz

from .utils.parser import text_parser
from .utils import report_builders
from .utils.data_processing import (
    processing_custom_field_data,
    )
from alm_vcard.serializer import serialize_objs
from almanet.utils.api import CommonMeta

import base64
import simplejson as json
from collections import OrderedDict
from .tasks import grouped_contact_import_task, check_task_status
import time


def _firstOfQuerySet(queryset):
    try :
        return queryset.all()[0]
    except IndexError:
        return None


def use_in_field(field_name):
    '''
        tastypie's 'use_in' keywarg used for:
             Optionally accepts ``use_in``. This may be one of ``list``, ``detail``
            ``all``
            or
            a callable which accepts a ``bundle`` and returns
            ``True`` or ``False``. Indicates wheather this field will be included
            during dehydration of a list of objects or a single object. If ``use_in``
            is a callable, and returns ``True``, the field will be included during
            dehydration.
            Defaults to ``all``.

        Example:
            see MobileStateResource, where passed to skip 'activities' in SalesCycles
            see SalesCycleResource, 'activities' CustomToManyField with this function
    '''
    def use_in(bundle):
        if hasattr(bundle, 'use_fields'):
            if field_name in getattr(bundle, 'use_fields'):
                return True
        return False
    return use_in


def skip_in_field(field_name):
    '''
        works as use_in_field but opposite
    '''
    def use_in(bundle):
        if hasattr(bundle, 'skip_fields'):
            if field_name in getattr(bundle, 'skip_fields'):
                return False
        return True
    return use_in


class CustomToManyField(fields.ToManyField):
    """
    used to add 'full_use_ids' flag for return objects 'ids' not 'resource_uri'
    """
    def __init__(self, to, attribute, related_name=None, default=None,
                 null=False, blank=False, readonly=False, full=False,
                 unique=False, help_text=None, use_in='all', full_list=True, full_detail=True,

                 full_use_ids=False
                 ):

        super(self.__class__, self).__init__(
            to, attribute, related_name=related_name, default=default,
            null=null, blank=blank, readonly=readonly, full=full,
            unique=unique, help_text=help_text, use_in=use_in,
            full_list=full_list, full_detail=full_detail
        )

        self.full_use_ids = full_use_ids


    def dehydrate_related(self, bundle, related_resource, for_list=True):
        """
        Based on the ``full_resource``, returns either the endpoint or the data
        from ``full_dehydrate`` for the related resource.

        CUSTOM:
            return 'id' as endpoint if full_use_ids
        """

        if self.full_use_ids:
            return related_resource.get_resource_id(bundle)
        else:
            return super(self.__class__, self).dehydrate_related(bundle, related_resource, for_list=for_list)


    def build_related_resource(self, value, request=None, related_obj=None, related_name=None):
        return super(self.__class__, self).build_related_resource(value, request=request,
            related_obj=related_obj, related_name=related_name)


class CRMServiceModelResource(ModelResource):

    def apply_filters(self, request, applicable_filters):
        '''
            first 'q' is filter for limit by company_id;
            additional filters (in one Q object) can be passed
            in applicable_filters as value of 'q'-key
        '''
        q = Q(company_id=request.company.id)

        custom_Q = applicable_filters.pop('q', None)  # 'q' - key for Q() object
        objects = super(ModelResource, self).apply_filters(request, applicable_filters)
        if custom_Q:
            q = q & custom_Q    
        return objects.filter(q)

    def hydrate(self, bundle):
        """
        bundle.request.user_env is empty dict{}
        because bundle.request.user is AnonymousUser
        it happen when tastypie uses BasicAuthentication or another
        which doesn't have session
        """
        user = bundle.request.user
        if user:
            bundle.obj.owner = user
            bundle.obj.company_id = bundle.request.company.id

        return bundle

    def get_bundle_list(self, obj_list, request):
        '''
        receives a queryset and returns a list of bundles
        '''
        objects = []
        for obj in obj_list:
            bundle = self.build_bundle(obj=obj, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)
        return objects

    def get_bundle_detail(self, obj, request):
        '''
        receives a object and returns a bundle
        '''
        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        return bundle

    def get_resource_id(self, bundle):
        return self.detail_uri_kwargs(bundle)[self._meta.detail_uri_name]

    class Meta:
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        authentication = MultiAuthentication(SessionAuthentication())
        authorization = Authorization()


class ContactResource(CRMServiceModelResource):
    '''
    GET Method \n
    I{URL}:  U{alma.net/api/v1/contact}\n
    
    Description:
    Api for Contact model\n

    POST Create Contact example\n
    ACCEPTS
    {
        author_id: 1
        children: []
        date_created: "2015-05-14T12:56:40.250227"
        global_sales_cycle: {activities:[], author_id:1, contact_id:2, date_created:2015-05-14T12:56:40.939332,…}
        id: 2
        owner: 1
        parent: null
        parent_id: null
        resource_uri: "/api/v1/contact/2/"
        sales_cycles: [3]
        0: 3
        share: {contact:2, date_created:2015-05-14T12:56:40.930951, id:1, is_read:false, note:Example Note,…}
        status: 0
        company_id: 1
        tp: "user"
        vcard: {additional_name:, adrs:[], agents:[], bday:null, categories:[], classP:null, custom_fields:[],…}
        additional_name: ""
        adrs: []
        agents: []
        bday: null
        categories: []
        classP: null
        custom_fields: []
        custom_sections: []
        emails: [{type:internet, value:example@example.com}, {type:home, value:example2@example.com}]
        0: {type:internet, value:example@example.com}
        1: {type:home, value:example2@example.com}
        family_name: ""
        fn: "Example Example"
        geos: []
        given_name: ""
        honorific_prefix: ""
        honorific_suffix: ""
        keys: []
        labels: []
        mailers: []
        nicknames: []
        notes: []
        orgs: [{organization_name:Company, organization_unit:}]
        rev: null
        roles: []
        sort_string: null
        tels: [{type:work, value:7777777777}]
        titles: [{data:SEO}]
        tzs: []
        uid: null
        urls: []
    }
    RESPONSE
    {
     "author_id": 1,
     "children": [],
     "date_created": "2015-05-14T12:56:40.250227",
     "global_sales_cycle":{},
     "id": 2,
     "owner": 1,
     "parent": null,
     "parent_id": null,
     "resource_uri": "/api/v1/contact/2/",
     "sales_cycles": [3],
     "share": {"contact": 2,
     "date_created": "2015-05-14T12:56:40.930951",
     "id": 1,
     "is_read": false,
     "note": "Example Note",
     "resource_uri": "/api/v1/share/1/",
     "share_from": 1,
     "share_to": 1},
     "status": 0,
     "company_id": 1,
     "tp": "user",
     "vcard": {
         "additional_name": "",
         "adrs": [],
         "agents": [],
         "bday": null,
         "categories": [],
         "classP": null,
         "custom_fields": [],
         "custom_sections": [],
         "emails": [{"type": "internet","value": "example@example.com"},{"type": "home", "value": "example2@example.com"}],
         "family_name": "",
         "fn": "Example Example",
         "geos": [],
         "given_name": "",
         "honorific_prefix": "",
         "honorific_suffix": "",
         "keys": [],
         "labels": [],
         "mailers": [],
         "nicknames": [],
         "notes": [],
         "orgs": [{"organization_name": "Company",
         "organization_unit": ""}],
         "rev": null,
         "roles": [],
         "sort_string": null,
         "tels": [{"type": "work", "value": "7777777777"}], 
         "titles": [{"data": "SEO"}], 
         "tzs": [], 
         "uid": null, 
         "urls": []
        }
     }

    PUT Edit Contact Example
    So basically if you want to edit the contact you must send all the attributes
    (except for the empty ones) If you want to say change fn (full name) and leave
    emails and telephone number untouched you have to send them via PUT as well. And
    if you want to add an email to a contact you have to attach the previous ones (they 
    may be edited as well, just keep ids of those objects) plus the new email object.
    The Accept and response json are similar to the ones used in Create example 

    @type  limit: number
    @param limit: The limit of results, 20 by default.
    @type  offset: number
    @param offset: The offset of results, 0 by default

    @return:  contacts

    >>> {
    ...     "assignees": [
    ...         "/api/v1/crmuser/1/"
    ...     ],
    ...     "date_created": "2014-09-10T00:00:00",
    ...     "followers": [],
    ...     "id": 1,
    ...     "owner": "/api/v1/crmuser/1/",
    ...     "resource_uri": "/api/v1/contact/1/",
    ...     "sales_cycles": [
    ...         "/api/v1/sales_cycle/1/",
    ...         "/api/v1/sales_cycle/2/",
    ...         "/api/v1/sales_cycle/3/"
    ...     ],
    ...     "status": 0,
    ...     "company_id": 1,
    ...     "tp": "user",
    ...     "vcard": {...}
    ... },


    @undocumented: prepend_urls, Meta
    '''
    vcard = fields.ToOneField('alm_vcard.api.VCardResource', 'vcard',
        null=True, full=True)
    owner = fields.ToOneField('alm_user.api.UserResource', 'owner',
        null=True, full=False)

    sales_cycles = CustomToManyField('alm_crm.api.SalesCycleResource', 'sales_cycles',
        null=True, full=False, full_use_ids=True)
    parent = fields.ToOneField(
        'alm_crm.api.ContactResource', 'parent',
        null=True, full=False
        )

    share = fields.ToOneField('alm_crm.api.ShareResource',
        attribute=lambda bundle: _firstOfQuerySet(bundle.obj.share_set),
        null=True, blank=True, readonly=True, full=False)

    owner_id = fields.IntegerField(attribute='owner_id', null=True)
    parent_id = fields.IntegerField(attribute='parent_id', null=True)

    class Meta(CommonMeta):
        queryset = Contact.objects.all().select_related(
            'owner', 'parent', 'vcard').prefetch_related(
                'sales_cycles', 'children', 'share_set',
                'vcard__tel_set', 'vcard__category_set',
                'vcard__adr_set', 'vcard__title_set', 'vcard__url_set',
                'vcard__org_set', 'vcard__email_set')
        resource_name = 'contact'
        filtering = {
            'status': ['exact'],
            'tp': ['exact'],
            'id': ALL
        }
        filtering.update(CommonMeta.filtering)

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/recent%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_contacted'),
                name='api_last_contacted'
            ),
            url(
                r"^(?P<resource_name>%s)/cold_base%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cold_base'),
                name='api_cold_base'
            ),
            url(
                r"^(?P<resource_name>%s)/leads%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_leads'),
                name='api_leads'
            ),
            url(
                r"^(?P<resource_name>%s)/search%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('search'),
                name='api_search'
            ),
            url(
                r"^(?P<resource_name>%s)/assign_contact%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('assign_contact'),
                name='api_assign_contact'
            ),
            url(
                r"^(?P<resource_name>%s)/assign_contacts%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('assign_contacts'),
                name='api_assign_contacts'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/products%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_products'),
                name='api_get_products'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/activities%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_activities'),
                name='api_get_activities'
            ),
            url(
                r"^(?P<resource_name>%s)/share_contact%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('share_contact'),
                name='api_share_contact'
            ),
            url(
                r"^(?P<resource_name>%s)/share_contacts%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('share_contacts'),
                name='api_share_contacts'
            ),
            url(
                r"^(?P<resource_name>%s)/import%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('import_contacts'),
                name='api_import_contacts_from_vcard'
            ),
            url(
                r"^(?P<resource_name>%s)/delete_contacts%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('delete_contacts'),
                name='api_delete_contacts_from_vcard'
            ),
            url(
                r"^(?P<resource_name>%s)/contacts_merge%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('contacts_merge'),
                name='api_contacts_merge'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/delete%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('delete_contact'),
                name='api_delete_contact'
            ),
            url(
                r"^(?P<resource_name>%s)/import_from_structure%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('import_from_structure'),
                name='api_import_from_structure'
            ),
            url(
                r"^(?P<resource_name>%s)/check_import_status%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_import_status'),
                name='api_check_import_status'
            ),
            url(
                r"^(?P<resource_name>%s)/state%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_contact_state'),
                name='api_get_contact_state'
            ),
            url(
                r"^(?P<resource_name>%s)/vcardstate%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_vcard_state'),
                name='api_get_vcard_state'
            )   
        ]

    def get_meta_dict(self, limit, offset, count, url):
        obj_dict = {}
        obj_dict['limit'] = limit
        obj_dict['offset'] = offset
        obj_dict['url'] = url

        obj_dict['next'] = self.get_next(limit, offset, count, url)
        obj_dict['previous'] = self.get_previous(limit, offset, url)

        return obj_dict

    def get_previous(self, limit, offset, url):
        if offset-limit < 0:
            return None
        if not url[len(url)-1] == '/':
            url+'/'
        return url+'?limit=%s&offset=%s' % (limit, offset-limit)

    def get_next(self, limit, offset, count, url):
        if offset + limit >= count:
            return None
        if not url[len(url)-1] == '/':
            url+'/'
        return url+'?limit=%s&offset=%s' % (limit, offset+limit)

    def obj_create(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)


        bundle = self.full_hydrate(bundle)
        if bundle.data.get('custom_fields', None):
            processing_custom_field_data(bundle.data['custom_fields'], bundle.obj)
        new_bundle = self.full_dehydrate(
                        self.build_bundle(
                            obj=Contact.objects.get(id=bundle.obj.id))
                        )
        new_bundle.data['global_sales_cycle'] = SalesCycleResource().full_dehydrate(
                SalesCycleResource().build_bundle(
                    obj=SalesCycle.objects.get(contact_id=bundle.obj.id)
                )
            )
        #return self.save(bundle, skip_errors=skip_errors)
        raise ImmediateHttpResponse(
            HttpResponse(
                content=Serializer().to_json(new_bundle),
                content_type='application/json; charset=utf-8', status=200
                )
            )
        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        if not bundle.obj or not self.get_bundle_detail_data(bundle):
            try:
                lookup_kwargs = self.lookup_kwargs_with_identifiers(bundle, kwargs)
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle=bundle, **lookup_kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")


        bundle = self.full_hydrate(bundle, **kwargs)
        #return self.save(bundle, skip_errors=skip_errors)
        if bundle.data.get('custom_fields', None):
            processing_custom_field_data(bundle.data['custom_fields'], bundle.obj)
        raise ImmediateHttpResponse(
            HttpResponse(
                content=Serializer().to_json(
                    self.full_dehydrate(
                        self.build_bundle(
                            obj=Contact.objects.get(id=bundle.obj.id))
                        )
                    ),
                content_type='application/json; charset=utf-8', status=200
                )
            )
        return bundle

    def full_dehydrate(self, bundle, for_list=False):
        '''Custom representation of followers, assignees etc.'''
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=for_list)
        bundle.data['children'] = [contact.id for contact in bundle.obj.children.all()]
        bundle.data['custom_fields'] = {}
        for field in bundle.obj.custom_field_values.all():
            bundle.data['custom_fields'][field.custom_field.id] = field.value

        return bundle

    # def dehydrate_assignees(self, bundle):
    #     return [assignee.pk for assignee in bundle.obj.assignees.all()]

    # def dehydrate_followers(self, bundle):
    #     return [follower.pk for follower in bundle.obj.followers.all()]

    def dehydrate_owner(self, bundle):
        return bundle.obj.owner.id

    def hydrate_sales_cycles(self, bundle):
        for sales_cycle in bundle.data.get('sales_cycles', []):
            bundle.obj.sales_cycles.add(
                SalesCycle.objects.get(
                    id=int(sales_cycle)
                    )
                )
        return bundle

    def hydrate_parent(self, bundle):
        parent_id = bundle.data.get('parent_id', "")
        if bundle.data.get('parent_id', ""):
            bundle.obj.parent = Contact.objects.get(id=int(parent_id))
        else:
            bundle.obj.parent=None
        children = bundle.data.get('children', [])
        bundle.obj.children.clear()
        for child in children:
            bundle.obj.children.add(Contact.objects.get(id=child))
        return bundle


    def full_hydrate(self, bundle, **kwargs):
        # t1 = time.time()
        vcard_instance = ast.literal_eval(
                str(
                    bundle.data.get('vcard', '{}')
                    )
                )
        if not vcard_instance.get('fn') and not vcard_instance.get('given_name') and not vcard_instance.get('family_name'):
            raise Exception
        contact_id = kwargs.get('pk', None)
        company_id = bundle.request.user.get_account(bundle.request).company.id
        if contact_id:
            bundle.obj = Contact.objects.get(id=int(contact_id))
            bundle.obj.company_id = company_id
        else:
            bundle.obj = self._meta.object_class()
            bundle.obj.company_id = company_id
            bundle.obj.owner_id = bundle.request.user.id
            bundle.obj.save()

        '''
        Go through all field names in the Contact Model and check with
        the json that has been submitted. So if the attribute is there
        then i use bundle.obj and setattr of current field_name to whatever
        i got in a json. If its missing then i just delete it.

        '''
        bundle = self.hydrate_sales_cycles(bundle)
        bundle = self.hydrate_parent(bundle)
        if bundle.data.get('user_id', ""):
            bundle.obj.owner_id = int(bundle.data['user_id'])
        # if bundle.data.get('parent_id',""):
        #     bundle.obj.parent_id = int(bundle.data['parent_id'])
        field_names = bundle.obj._meta.get_all_field_names()
        field_names.remove('parent')
        field_names.remove('children')
        field_names.remove('sales_cycles')
        field_names.remove('share_set')
        for field_name in field_names:
            if bundle.data.get(str(field_name), None):
                try:
                    field_object = ast.literal_eval(bundle.data.get(str(field_name), None))
                except:
                    field_object = bundle.data.get(field_name)
                if isinstance(field_object, unicode):
                    bundle.obj.__setattr__(field_name, field_object)
                elif isinstance(field_object, list):
                    for obj in field_object:
                        bundle.obj.__getattribute__(field_name).add(int(obj))
                elif isinstance(field_object, dict) :
                    vcard_bundle = VCardResource().build_bundle(
                        data=field_object,
                        request=bundle.request
                        )
                    if kwargs.get('pk', None):
                        vcard_bundle = VCardResource().obj_create(
                            bundle=vcard_bundle,
                            skip_errors=False,
                            **kwargs
                            )
                    else:
                        vcard_bundle = VCardResource().obj_create(
                            bundle=vcard_bundle,
                            **kwargs
                            )
        # t2=time.time()-t1
        # print "Time to finish contact hydration %s" % t2
        bundle.obj.vcard = vcard_bundle.obj
        # t3=time.time()-t2
        # print "Time to finish vcard hydration %s" % t3
        bundle.obj.save()
        with transaction.atomic():
            if bundle.data.get('note') and not kwargs.get('pk'):
                share = bundle.obj.create_share_to(
                    bundle.request.user.id,
                    company_id,
                    bundle.data.get('note'))
                text_parser(base_text=share.note, content_class=share.__class__,
                    object_id=share.id, company_id = bundle.request.user.get_account(bundle.request).company.id)
            if not kwargs.get('pk'):
                SalesCycle.create_globalcycle(
                    **{
                     'company_id':company_id,
                     'owner_id':bundle.request.user.id,
                     'contact_id':bundle.obj.id
                    }
                )
        return bundle

    def assign_company_contact(self, request, **kwargs):
        if kwargs.get('contact_id'):
            try:
                contact = Contact.objects.get(
                    id=int(kwargs.get('contact_id'))
                    )
            except:
                return self.create_response(
                    request, {'success':False, 'message':'Contact with such id does not exist'}
                    )
        if kwargs.get('company_contact_id'):
            try:
                company_contact = Contact.objects.get(
                    id=int(kwargs.get('company_contact_id'))
                    )
                if company_contact.tp == 'user':
                    return self.create_response(
                        request, {'success':False, 'message':'Company Contact with such id is not of company type'}
                        )
            except:
                return self.create_response(
                    request, {'success':False, 'message':'Company Contact with such id does not exist'}
                    )
        contact.parent_id = company_contact.id
        contact.save()
        return self.create_response(
                    request, {'success':True, 'message':'Contact has been assigned to a Company Contact'}
                    )

    def get_last_contacted(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/recent/}

        Description
        Api function to return contacts filtered by the last contact date

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default
        @type  include_activities: boolean
        @param include_activities: Boolean value indicating the inclusion of
                            activities in the result outputs. False by default.
        @type  owned: boolean
        @param owned: Boolean value indicating the inclusion of contacts
                owned by the user. True by default.
        @type  assigned: boolean
        @param assigned: Boolean value indicating the inclusion of contacts
                that are assigned to the user. False by default.
        @type  followed: boolean
        @param followed: Boolean value indicating the inclusion of contacts
                that user follows. False by default.

        @return:  contacts ordered by last_activity_date.

        >>> "objecs":[
        ...    {
        ...     "assignees": [
        ...         "/api/v1/crmuser/1/"
        ...     ],
        ...     "date_created": "2014-09-10T00:00:00",
        ...     "followers": [],
        ...     "id": 1,
        ...     "owner": "/api/v1/crmuser/1/",
        ...     "resource_uri": "/api/v1/contact/1/",
        ...     "sales_cycles": [
        ...         "/api/v1/sales_cycle/1/",
        ...         "/api/v1/sales_cycle/2/",
        ...         "/api/v1/sales_cycle/3/"
        ...     ],
        ...     "status": 0,
        ...     "company_id": 1,
        ...     "tp": "user",
        ...     "vcard": {...}
        ... },
        ... ]

        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        include_activities = bool(request.GET.get('include_activities', False))
        owned = bool(request.GET.get('owned', True))
        assigned = bool(request.GET.get('assigned', False))
        followed = bool(request.GET.get('followed', False))
        contacts = Contact.get_contacts_by_last_activity_date(
            company_id = request.user.get_account(request).company.id,
            user_id=request.user.id,
            include_activities=include_activities,
            )
        if not include_activities:
            return self.create_response(
                request,
                {
                'meta':self.get_meta_dict(limit, offset, len(contacts), 'api/v1/contact/'),
                'objects': self.get_bundle_list(contacts, request)}
                )
        else:
            '''
            returns
                (Queryset<Contact>,
                Queryset<Activity>,
                {
                    contact1_id: [activity1_id, activity2_id],
                    contact2_id: [activity3_id]
                })
            '''
            obj_dict = {}
            obj_dict['contacts'] = self.get_bundle_list(contacts[0], request)
            obj_dict['activities'] = self.get_bundle_list(contacts[1], request)
            obj_dict['dict'] = contacts[2]
            return self.create_response(request, obj_dict)

    def get_contact_state(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            base_bundle = self.build_bundle(request=request)
            contact_ids = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs)
                ).values_list('id', flat=True)
            contacts = Contact.get_by_ids(*contact_ids)
            # bundles = (
            #     {
            #         'id': obj.id,
            #         'author_id': obj.owner_id,
            #         'date_created': obj.date_created,
            #         'date_edited': obj.date_edited,
            #         'owner': obj.owner_id,
            #         'parent_id': obj.parent_id,
            #         'status': obj.status,
            #         'tp': obj.tp,
            #         'company_id': obj.company_id,
            #         'children': list(contact.id for contact in obj.children.all()),
            #         'sales_cycles': list(cycle.id for cycle in obj.sales_cycles.all()),
            #         'vcard_id': obj.vcard_id
            #     } for obj in objects)
        return self.create_response(request, contacts)

    def get_vcard_state(self, request, **kwargs):
        t1 = time.time()

        with RequestContext(self, request, allowed_methods=['get']):
            base_bundle = self.build_bundle(request=request)
            vcard_ids = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs)).values_list('vcard_id', flat=True)
            return self.create_response(request, VCard.get_by_ids(*vcard_ids))

    def get_cold_base(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/cold_base/}

        Description
        Api function to return contacts that have not been contacted yet

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default

        @return: contacts that have no salescycles and activities.

        >>> "objects":[
        ... {
        ... "assignees": [
        ...     "/api/v1/crmuser/1/"
        ... ],
        ... "date_created": "2014-09-10T00:00:00",
        ... "followers": [],
        ... "id": 1,
        ... "owner": "/api/v1/crmuser/1/",
        ... "resource_uri": "/api/v1/contact/1/",
        ... "sales_cycles": [
        ...     "/api/v1/sales_cycle/1/",
        ...     "/api/v1/sales_cycle/2/",
        ...     "/api/v1/sales_cycle/3/"
        ... ],
        ... "status": 0,
        ... "company_id": 1,
        ... "tp": "user",
        ... "vcard": {...}
        ... },
        ... ]

        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        contacts = Contact.get_cold_base(request.user.id)
        return self.create_response(
            request,
            {
                'meta': {
                    'limit': limit,
                    'offset': offset
                },
                'objects': self.get_bundle_list(contacts, request)
            })

    def get_leads(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/leads/}

        Description
        Api function to return contacts that have a status of LEAD

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default

        @return: contacts.

        >>> "objects": [
        ...   {
        ...     "assignees": [
        ...         "/api/v1/crmuser/1/"
        ...     ],
        ...     "date_created": "2014-09-10T00:00:00",
        ...     "followers": [],
        ...     "id": 1,
        ...     "owner": "/api/v1/crmuser/1/",
        ...     "resource_uri": "/api/v1/contact/1/",
        ...     "sales_cycles": [
        ...         "/api/v1/sales_cycle/1/",
        ...         "/api/v1/sales_cycle/2/",
        ...         "/api/v1/sales_cycle/3/"
        ...     ],
        ...     "status": 0,
        ...     "company_id": 1,
        ...     "tp": "user",
        ...     "vcard": {...}
        ... },
        ... ]

        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        contacts = Contact.get_contacts_by_status(request.user.id,
                                                  Contact.LEAD)
        return self.create_response(
            request, {
                'objects': self.get_bundle_list(contacts, request)
            })

    def get_products(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/products/}

        Description
        Api function to return products associated with that contact

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default

        @return: list of products associated with this contact.

        >>> "objects": [
        ... {
        ...     currency": "KZT",
        ...     "description": "Paragraph Online is product for lawyers",
        ...     "id": 4,
        ...     "name": "p2: Paragraph Online",
        ...     "price": 59000,
        ...     "resource_uri": "/api/v1/product/4/",
        ...     "sales_cycles": [
        ...         "/api/v1/sales_cycle/1/",
        ...         "/api/v1/sales_cycle/4/",
        ...         "/api/v1/sales_cycle/6/",
        ...         "/api/v1/sales_cycle/18/",
        ...         "/api/v1/sales_cycle/20/",
        ...         "/api/v1/sales_cycle/21/",
        ...         "/api/v1/sales_cycle/22/",
        ...         "/api/v1/sales_cycle/23/"
        ...     ],
        ...     "company_id": null
        ...     },
        ... ]

        '''
        contact_id = kwargs.get('id')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        products = Contact.get_contact_products(contact_id)

        obj_dict = {}
        obj_dict['meta'] = {
                'limit': limit,
                'offset': offset
            },
        obj_dict['objects'] = ProductResource().get_bundle_list(products, request)
        return self.create_response(request, obj_dict)

    def get_activities(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/activities/}

        Description
        Api function to return activities associated with that contact

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default

        @return: list of activities associated with this contact.

        >>> "objects": [
        ... {
        ...     "date_created": "2014-03-19T00:00:00",
        ...     "date_edited": true,
        ...     "description": "activity #10 of SalesCycle #3",
        ...     "id": 30,
        ...     "owner": null,
        ...     "resource_uri": "/api/v1/activity/30/",
        ...     "sales_cycle": "/api/v1/sales_cycle/3/",
        ...     "company_id": null,
        ...     "title": "activity #10 of SalesCycle #3"
        ... },

        '''
        contact_id = kwargs.get('id')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        activities = Contact.get_contact_activities(contact_id)
        obj_dict = {}
        obj_dict['meta'] = {
                'limit': limit,
                'offset': offset
            },
        obj_dict['objects'] = ActivityResource().get_bundle_list(activities, request)
        return self.create_response(request, obj_dict)

    def search(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/search/}

        Description
        Api implementation of search, pass search_params in this format:
        [('fn', 'startswith'), ('org__organization_unit', 'icontains'), 'bday']
        will search by the beginning of fn if search_params are not provided
        ast library f-n literal_eval converts the string representation of a
        list to a python list, will search by ('fn','startswith') by default
        pass limit and offset through GET request

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default
        @type  search_text: string
        @param search_text: The text you want to search by
        @type  search_params: list of tuples
        @param search_params: The search params you want to include in your
                            search.
        @type  order_by: list
        @param order_by: A list consisting of 2 elements, first one is
                    parameter like fn, or email__value. The second one is order,
                    'asc' or 'desc'. ['fn','asc'] by default


        @return: list of contacts.

        >>> "objects": [
        ... {
        ...     "assignees": [],
        ...     "date_created": "2014-11-18T09:20:23.359796",
        ...     "followers": [],
        ...     "id": 12,
        ...     "owner": null,
        ...     "resource_uri": "/api/v1/contact/12/",
        ...     "sales_cycles": [],
        ...     "status": 0,
        ...     "company_id": null,
        ...     "tp": "user",
        ...     "vcard": {}
        ... },
        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        search_text = request.GET.get('search_text', '').encode('utf-8')
        search_params = ast.literal_eval(
            request.GET.get('search_params', "[('fn', 'startswith')]"))
        order_by = ast.literal_eval(request.GET.get('order_by', "['fn','asc']"))
        contacts = Contact.filter_contacts_by_vcard(
            company_id=bundle.request.user.get_account(bundle.request).company.id,
            search_text=search_text,
            search_params=search_params,
            order_by=order_by)
        return self.create_response(
            request, {
                'objects': self.get_bundle_list(contacts, request)
            })

    def share_contact(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/share_contact/}

        Description
        Share a contact with a user

        @type  share_to: number
        @param share_to: Id of a user to share a contact with
        @type  share_from: number
        @param share_from: Id of a user who is sharing a contact
        @type  contact_id: number
        @param contact_id: Id of a desired contact


        @return: json.

        >>>
        ... {
        ...     'success':True
        ... },
        '''
        share_to = int(request.GET.get('share_to', 0))
        if not share_to:
            return self.create_response(
                request,
                {'success': False,
                'error_message': "You didn't specify with whom you want to share contact(s)"
                }
                )
        share_from = int(request.GET.get('share_from', 0))
        if not share_from:
            return self.create_response(
                request,
                {'success': False,
                'error_message': "You didn't specify the user whos sharing contact(s)"
                }
                )
        contact_id = int(request.GET.get('contact_id', 0))
        text_parser(base_text=share.note, content_class=share.__class__,
                    object_id=share.id, company_id = bundle.request.user.get_account(bundle.request).company.id)
        return self.create_response(
            request,
            {'success':
                Contact.share_contact(share_from, share_to, contact_id, company_id=request.user.get_account(request).company.id)}
            )

    def share_contacts(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/share_contacts/}

        Description
        Share multiple contact with a user

        @type  share_to: number
        @param share_to: Id of a user to share a contact with
        @type  share_from: number
        @param share_from: Id of a user who is sharing a contact
        @type  contact_id: list
        @param contact_id: list of contact ids to be shared


        @return: json.

        >>>
        ... {
        ...     'success':True
        ... },

        '''
        share_to = int(request.GET.get('share_to',0))
        if not share_to:
            return self.create_response(
                request,
                {'success': False,
                 'error_message': "You didn't specify with whom you want to share contact(s)"
                 }
                )
        share_from = int(request.GET.get('share_from', 0))
        if not share_from:
            return self.create_response(
                request,
                {'success': False,
                 'error_message': "You didn't specify the user whos sharing contact(s)"
                 }
                )
        contact_ids = ast.literal_eval(request.GET.get('contact_ids', []))
        return self.create_response(
            request,
            {'success':
                Contact.share_contacts(share_from, share_to, contact_ids)}
            )

    def import_contacts(self, request, **kwargs):
        '''
        POST METHOD
        I{URL}:  U{alma.net/api/v1/contact/import_contacts_from_vcard/}
        Description
        Import contacts from a vcard file
        @type  my_file: file
        @param my_file: A vcard file
        @return: json.
        >>>
        ... {
        ...    'success':True,
        ...    'contact_ids':[
        ...            91,
        ...            92,
        ...            93,
        ...        ],
        ... },
        '''
        objects = []
        contact_resource = ContactResource()
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        current_user = request.user.get_account(request).company
        decoded_string = base64.b64decode(data['uploaded_file'])
        filename_chunks = data['filename'].split('.')
        filename = filename_chunks[len(filename_chunks)-1]
        if filename=='csv':
            contacts = Contact.import_from_csv(
                decoded_string, request.user)
            if type(contacts) == tuple:
                self.log_throttled_access(request)
                data = {'success': False, 'error':"Ошибка в ячейке %s в %s-ом ряду." % contacts}
                return self.error_response(request, data, response_class=http.HttpBadRequest)
            if not contacts:
                self.log_throttled_access(request)
                return self.error_response(request, {'success': False}, response_class=http.HttpBadRequest)
            contact_list = ContactList(
                owner = request.user.get_account(request).company,
                title = data['filename'])
            contact_list.save()
            contact_list.contacts = contacts
            for contact in contacts:
                _bundle = contact_resource.build_bundle(
                    obj=contact, request=request)
                _bundle.data['global_sales_cycle'] = SalesCycleResource().full_dehydrate(
                    SalesCycleResource().build_bundle(
                        obj=SalesCycle.objects.get(contact_id=contact.id)
                    )
                )
                objects.append(contact_resource.full_dehydrate(
                    _bundle, for_list=True))
            contact_list = ContactListResource().full_dehydrate(
                ContactListResource().build_bundle(
                    obj=contact_list
                    )
                )
        elif filename=='xls' or filename=='xlsx':
            xls_meta = Contact.get_xls_structure(data['filename'], decoded_string)
            xls_meta['type'] = 'excel'
            return self.create_response(
                request, xls_meta)
        elif filename=='vcf':
            contacts = Contact.import_from_vcard(
                    decoded_string, current_user)
            if not contacts:
                self.log_throttled_access(request)
                return self.error_response(request, {'success': False}, response_class=http.HttpBadRequest)
                # return self.create_response(request, {'success': False})
            if len(contacts)>1:
                contact_list = ContactList(
                    owner = request.user.get_account(request).company,
                    title = data['filename'])
                contact_list.save()
                contact_list.contacts = contacts
            else:
                contact_list = False
            for contact in contacts:
                share = contact.create_share_to(current_user.pk, company_id=current_user.get_account(request).company.id)
                text_parser(base_text=share.note, content_class=share.__class__,
                    object_id=share.id, company_id = request.user.get_account(request).company.id)
                _bundle = contact_resource.build_bundle(
                    obj=contact, request=request)
                _bundle.data['global_sales_cycle'] = SalesCycleResource().full_dehydrate(
                    SalesCycleResource().build_bundle(
                        obj=SalesCycle.objects.get(contact_id=contact.id)
                    )
                )
                objects.append(contact_resource.full_dehydrate(
                    _bundle, for_list=True))
            if contact_list:
                contact_list = ContactListResource().full_dehydrate(
                    ContactListResource().build_bundle(
                        obj=contact_list
                        )
                    )
        self.log_throttled_access(request)
        return self.create_response(
            request, {'objects': objects, 'contact_list': contact_list})

    def delete_contacts(self, request, **kwargs):
        """
        POST METHOD
        example
        send {'ids':[1,2,3]}
        """
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            obj_ids = data.get('ids', "")
            objects = Contact.delete_contacts(obj_ids)
            return self.create_response(request, {'objects':objects}, response_class=http.HttpAccepted)

    def delete_contact(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            objects = Contact.delete_contacts([kwargs.get('id')])
            objects['contact'] = int(objects['contacts'][0]) if len(objects['contacts']) > 0 else None
            objects.pop('contacts')
            return self.create_response(request, {'objects':objects}, response_class=http.HttpAccepted)

    def contacts_merge(self, request, **kwargs):
        """
        POST METHOD
        example
        {"merged_contacts":[1,2,3], "merge_into_contact":1, "delete":True/False}
        """
        data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        # print request.body
        # data = eval(request.body)
        merged_contacts_ids = data.get("merged_contacts", [])
        merge_into_contact_id = data.get("merge_into_contact", "")
        delete_merged = data.get("merged_contacts", [])
        if not merged_contacts_ids or not merge_into_contact_id:
            return self.create_response(
                        request, {'success':False, 'message':'Contact ids have not been appended'}
                        )
        try:
            primary_object = Contact.objects.get(id=merge_into_contact_id)
        except ObjectDoesNotExist:
            return self.create_response(
                    request, {
                        'success':False, 
                        'message':'Contact with %s id doesnt exist' % merge_into_contact_id
                        }
                    )
        alias_objects = Contact.objects.filter(id__in=merged_contacts_ids)
        response = primary_object.merge_contacts(alias_objects, delete_merged)
        if not response['success']:  
            return self.create_response(
                request, response
                )
        t = time.time()
        contact = ContactResource().full_dehydrate(
            ContactResource().build_bundle(
                obj=response['contact'], request=request
                ), for_list=False
            )
        sales_cycles = [
            SalesCycleResource().full_dehydrate(
                SalesCycleResource().build_bundle(
                    obj=sales_cycle, request=request
                    ), for_list=True
                )  for sales_cycle in response['sales_cycles']
        ]
        activities = [
            ActivityResource().full_dehydrate(
                ActivityResource().build_bundle(
                    obj=activity, request=request
                    ), for_list=True
                )  for activity in response['activities']
        ]
        shares = [
            ShareResource().full_dehydrate(
                ShareResource().build_bundle(
                    obj=share, request=request
                    ), for_list=True
                )  for share in response['shares']
        ]
        # print "Time to dehydrate resources %s " % str(time.time()-t)
        return self.create_response(
                request,
                {
                 'contact':contact,
                 'deleted_contacts_ids':response['deleted_contacts_ids'],
                 'deleted_sales_cycle_ids':response['deleted_sales_cycle_ids'],
                 'sales_cycles':sales_cycles,
                 'activities':activities,
                 'shares':shares,
                 'success':True
                }
            )

    def import_from_structure(self, request, **kwargs):
        data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        col_structure = data.get('col_structure')
        filename = data.get('filename')
        ignore_first_row = data.get('ignore_first_row',"")
        if not ignore_first_row:
            ignore_first_row = False
        # col_structure = request.body.get('col_structure')
        # filename = request.body.get('filename')
        # try:
        #     body = json.loads(request.body)
        # except Exception, e:
        #     pass
        # col_structure = body['col_structure']
        # filename = body['filename']
        if not col_structure or not filename:
            return self.create_response(
                request, {'success':False, 'message':'Invalid parameters'}
                )
        """
        col structure: 
        {0:'Adr__postal', 1:'VCard__fn', 2:'Adr__home', 3:'Org', 4:'Nickname'}
        """
        col_hash = []
        for key, value in col_structure.viewitems():
            obj_dict = {'num':key}
            obj_dict['model'] = value.split('__')[0]
            if len(value.split('__'))>1:
                obj_dict['attr'] = value.split('__')[1]
            col_hash.append(obj_dict)
        import_task_id = grouped_contact_import_task(
            col_hash, filename, request.user, request.user.get_account(request).company.id, request.user.get_account(request).email, ignore_first_row)
        return self.create_response(
            request, {'success':True,'task_id':import_task_id}
            )

    def check_import_status(self, request, **kwargs):
        objects = []
        contact_resource = ContactResource()
        # self.method_check(request, allowed=['get'])
        # self.is_authenticated(request)
        # self.throttle_check(request)
        task_id = request.GET.get('task_id', "")
        if not task_id:
            return self.create_response(
                request, {'success':False, 'message':'No task was entered'}
                )
        if not check_task_status(task_id):
            return self.create_response(
                request, {'success':False, 'status':'PENDING'}
                )
        try:
            import_task = ImportTask.objects.get(uuid=task_id)
        except ObjectDoesNotExist:
            return self.create_response(
                request, {'success':False, 'message':'The task with particular id does not exist'}
                )
        contacts = import_task.contacts.all()
        contact_list = import_task.contactlist
        for contact in contacts:
            _bundle = contact_resource.build_bundle(
                obj=contact, request=request)
            _bundle.data['global_sales_cycle'] = SalesCycleResource().full_dehydrate(
                SalesCycleResource().build_bundle(
                    obj=SalesCycle.objects.get(contact_id=contact.id)
                )
            )
            objects.append(contact_resource.full_dehydrate(
                _bundle, for_list=True))
        contact_list = ContactListResource().full_dehydrate(
            ContactListResource().build_bundle(
                obj=contact_list
                )
            )
        imported_num = import_task.imported_num
        not_imported_num = import_task.not_imported_num
        email_sent = True if not_imported_num != 0 else False
        import_task.delete()
        return self.create_response(
            request, {'success':True, 'status':'FINISHED', 'objects': objects, 'contact_list': contact_list, 
            'imported_num':imported_num, 'not_imported_num':not_imported_num, 'email_sent':email_sent})


class SalesCycleResource(CRMServiceModelResource):
    '''
    GET Method
    I{URL}:  U{alma.net/api/v1/sales_cycle}\n
    B{Response}\n
    C{{"activities": [], "author_id": 1, "contact_id": 1, "date_created": "2015-05-14T11:47:26.545833", "description": "", "id": 2, "is_global": false, "log": [], "milestone_id": null, "projected_value": null, "real_value": null, "resource_uri": "/api/v1/sales_cycle/2/", "stat": [], "status": "P", "company_id": 1, "title": "New Cycle"}}\n
    
    B{Description}:
    API resource manage Contact's SalesCycles
    

    I{POST}\n
    B{Accepts Example}
    C{{author_id: 1, contact_id: 1, status: "N", title: "New Cycle"}}\n 
    B{Returns Example}
    C{{"activities": [], "author_id": 1, "contact_id": 1, "date_created": "2015-05-14T11:47:26.545833", "description": "", "id": 2, "is_global": false, "log": [], "milestone_id": null, "obj_created": true, "projected_value": null, "real_value": null, "resource_uri": "/api/v1/sales_cycle/2/", "stat": [], "status": "N", "company_id": 1, "title": "New Cycle"}} 
    
    I{PUT}\n
    B{Accepts Example}
    C{"status":"P"}\n
    B{Returns Example}
    C{"activities": [], "author_id": 1, "contact_id": 1, "date_created": "2015-05-14T11:47:26.545833", "description": "", "id": 2, "is_global": false, "log": [], "milestone_id": null, "obj_created": true, "projected_value": null, "real_value": null, "resource_uri": "/api/v1/sales_cycle/2/", "stat": [], "status": "N", "company_id": 1, "title": "New Cycle"}\n

    @undocumented: prepend_urls, Meta
    '''
    contact_id = fields.IntegerField(attribute='contact_id', null=True)
    activities = CustomToManyField('alm_crm.api.ActivityResource', 'rel_activities',
        related_name='sales_cycle', null=True, full=False, full_use_ids=True,
        use_in=skip_in_field('activities'))
    activities_count = fields.IntegerField(attribute='activities_count', readonly=True,
        use_in=use_in_field('activities_count'))
    product_ids = CustomToManyField('alm_crm.api.ProductResource', 'products',
        null=True, full=False, full_use_ids=True, readonly=True)
    owner_id = fields.IntegerField(attribute='owner_id')
    projected_value = fields.ToOneField('alm_crm.api.ValueResource',
                                        'projected_value', null=True,
                                        full=True)
    real_value = fields.ToOneField('alm_crm.api.ValueResource',
                                   'real_value', null=True, full=True)

    stat = fields.ToManyField('alm_crm.api.SalesCycleProductStatResource', 'product_stats',
        null=True, blank=True, readonly=True, full=True)
    milestone_id = fields.IntegerField(null=True, attribute='milestone_id')
    log = fields.ToManyField('alm_crm.api.SalesCycleLogEntryResource', 'log', null=True, full=True)

    class Meta(CommonMeta):
        queryset = SalesCycle.objects.all().prefetch_related('product_stats', 'products', 'product_stats__product', 'rel_activities', 'log')
        resource_name = 'sales_cycle'
        excludes = ['from_date', 'to_date']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        always_return_data = True

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/close/(?P<status>\w+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('close'),
                name='api_close'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/products%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('products'),
                name='api_products'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/change_milestone%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('change_milestone'),
                name='api_change_milestone'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/delete%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('delete_sales_cycle'),
                name='api_delete_sales_cycle'
            ),
        ]

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(self.__class__, self).build_filters(filters=filters)

        if 'limit_for' in filters:
            if filters['limit_for'] == 'mobile':
                orm_filters.update({
                    'is_global': False,
                    'status__in': [SalesCycle.NEW, SalesCycle.PENDING]
                    })

        return orm_filters

    def close(self, request, **kwargs):
        '''
        PUT METHOD
        I{URL}:  U{alma.net/api/v1/sales_cycle/:id/close/}

        B{Description}:
        close SalesCycle, set value of SalesCycleProductStat
        update status to 'C'('Completed')

        @return: updated SalesCycle

        '''
        with RequestContext(self, request, allowed_methods=['post', 'get', 'put']):
            basic_bundle = self.build_bundle(request=request)
            # get sales_cycle
            try:
                obj = SalesCycle.objects.get(id=kwargs['id'])
            except ObjectDoesNotExist:
                return http.HttpNotFound()
            except MultipleObjectsReturned:
                return http.HttpMultipleChoices(
                    "More than one resource is found at this URI.")
            if obj.is_global:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized(
                                            'Could not close global sales cycle'))
            bundle = self.build_bundle(obj=obj, request=request)

            # get PUT's data from request.body
            deserialized = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            deserialized = self.alter_deserialized_list_data(request, deserialized)
            if kwargs['status'] == 'succeed':
                sales_cycle, log_entry = bundle.obj.close(products_with_values=deserialized, 
                                                            company_id=request.user.get_account(request).company.id,
                                                            succeed=True)
                log_entry.owner = request.user
                log_entry.company_id = request.user.get_account(request).company.id
                log_entry.save()
            elif kwargs['status'] == 'fail':
                sales_cycle, log_entry = bundle.obj.close(products_with_values=deserialized, 
                                                            company_id=request.user.get_account(request).company.id,
                                                            succeed=False)
                log_entry.owner = request.user
                log_entry.company_id = request.user.get_account(request).company.id
                log_entry.save()
            else:
                return http.HttpBadRequest()

        return self.create_response(
            request, {
                'sales_cycle': SalesCycleResource().get_bundle_detail(sales_cycle, request)
            },
            response_class=http.HttpAccepted)

    def products(self, request, **kwargs):
        '''
        PUT METHOD
        I{URL}:  U{alma.net/api/v1/sales_cycle/:id/products/}

        B{Description}:
        replace products of the sales cycle
        @type  product_ids: list
        @param product_ids: product_ids which should be set, for instace [1,2,3]

        @return: updated SalesCycle

        '''
        with RequestContext(self, request, allowed_methods=['post', 'get', 'put']):
            basic_bundle = self.build_bundle(request=request)
            try:
                obj = self.cached_obj_get(bundle=basic_bundle,
                                          **self.remove_api_resource_names(kwargs))
            except ObjectDoesNotExist:
                return http.HttpNotFound()
            except MultipleObjectsReturned:
                return http.HttpMultipleChoices(
                    "More than one resource is found at this URI.")
            bundle = self.build_bundle(obj=obj, request=request)

            get_product_ids = lambda: {'object_ids': list(obj.products.values_list('pk', flat=True))}

            if request.method == 'GET':
                return self.create_response(request, get_product_ids())

            # get PUT's data from request.body
            deserialized = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            deserialized = self.alter_deserialized_list_data(request, deserialized)

            new_objects_list = deserialized['object_ids']
            last_objects_list = obj.products.all().values_list('id', flat=True)
            
            added = [Product.objects.get(id=item).name for item in new_objects_list if item not in last_objects_list]
            deleted = [Product.objects.get(id=item).name for item in last_objects_list if item not in new_objects_list]
            products = []

            obj.products.clear()
            obj.add_products(deserialized['object_ids'], company_id=request.user.get_account(request).company.id)

            for product in obj.products.all():
                products.append(
                    {
                        'id': product.id,
                        'name': product.name
                    }
                )

            meta = {"added": added,
                    "deleted": deleted,
                    "products": products}
            log_entry = SalesCycleLogEntry(sales_cycle=obj, 
                                            owner=request.user,
                                            company_id=request.user.get_account(request).company.id,
                                            entry_type=SalesCycleLogEntry.PC,
                                            meta=json.dumps(meta))
            log_entry.save()

            bundle = get_product_ids()
            bundle['log'] = SalesCycleLogEntryResource().get_bundle_detail(log_entry, request)

            if not self._meta.always_return_data:
                return http.HttpAccepted(location=location)
            else:
                return self.create_response(request, bundle,
                                            response_class=http.HttpAccepted)

    def change_milestone(self, request, **kwargs):
        '''
        POST METHOD
        I{URL}:  U{alma.net/api/v1/sales_cycle/:id/change_milestone/}

        B{Description}:
        change milestone of the sales cycle, creates SalesCycleLogEntry record with entry_type = MC

        @return: updated SalesCycle

        '''
        with RequestContext(self, request, allowed_methods=['post']):
            basic_bundle = self.build_bundle(request=request)
            try:
                obj = self.cached_obj_get(bundle=basic_bundle,
                                          **self.remove_api_resource_names(kwargs))
            except ObjectDoesNotExist:
                return http.HttpNotFound()
            except MultipleObjectsReturned:
                return http.HttpMultipleChoices(
                    "More than one resource is found at this URI.")
            bundle = self.build_bundle(obj=obj, request=request)

            # get PUT's data from request.body
            deserialized = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))

            sales_cycle = obj.change_milestone(user=request.user,
                                               milestone_id=deserialized['milestone_id'],
                                               company_id=request.user.get_account(request).company.id)

            if not self._meta.always_return_data:
                return http.HttpAccepted()
            else:
                return self.create_response(request, {
                    'sales_cycle': SalesCycleResource().get_bundle_detail(
                        SalesCycle.objects.get(id=sales_cycle.id), request),
                },
                response_class=http.HttpAccepted)

    def delete_sales_cycle(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/sales_cycle/:id/delete/}

        B{Description}:
        delete sales cycle and add in response deleted sales cycle id and related activities ids

        @return: deleted SalesCycle id and related Activities ids

        '''
        with RequestContext(self, request, allowed_methods=['get']):
            try:
                sales_cycle = SalesCycle.objects.get(pk=kwargs.get('id'))
                if sales_cycle.is_global:
                    return http.HttpBadRequest()
            except SalesCycle.DoesNotExist:
                return http.HttpNotFound()

            objects = {}
            objects['sales_cycle'] = sales_cycle.id
            objects['activities'] = list(sales_cycle.rel_activities.all().values_list('id', flat=True))
            sales_cycle.delete()
            return self.create_response(request, {'objects': objects}, response_class=http.HttpAccepted)

    def obj_create(self, bundle, **kwargs):
        bundle = super(self.__class__, self).obj_create(bundle, **kwargs)
        # if 'milestone_id' in bundle.data:
        #     milestone = Milestone.objects.get(pk=bundle.data.get('milestone_id'))
        #     bundle.obj.milestone = milestone

        # bundle.obj.save()
        # bundle = self.full_hydrate(bundle)
        # bundle = 
        bundle = self.save(bundle)
        bundle.data['obj_created'] = True
        return bundle

    def obj_update(self, bundle, **kwargs):
        del(bundle.data['activities'])
        return super(self.__class__, self).obj_update(bundle, **kwargs)

    def save(self, bundle, **kwargs):
        bundle = super(SalesCycleResource, self).save(bundle, **kwargs)
        if 'milestone_id' in bundle.data and bundle.data['milestone_id'] is not None:
            milestone = Milestone.objects.get(pk=bundle.data.get('milestone_id'))
            bundle.obj.milestone = milestone
        bundle.obj.save()
        return bundle


class SalesCycleLogEntryResource(CRMServiceModelResource):

    owner = fields.IntegerField(attribute='owner_id')

    class Meta(CommonMeta):
        queryset = SalesCycleLogEntry.objects.all()
        resource_name = 'sales_cycle_log_entry'
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        always_return_data = True


class MilestoneResource(CRMServiceModelResource):

    class Meta(CommonMeta):
        queryset = Milestone.objects.all().prefetch_related('sales_cycles')
        resource_name = 'milestone'
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        always_return_data = True

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/bulk_edit%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('bulk_edit'),
                name='api_bulk_edit'
            ),
            url(
                r"^(?P<resource_name>%s)/update%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('update'),
                name='api_update'
            )
        ]

    def bulk_edit(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            milestones = Milestone.objects.filter(company_id=request.user.get_account(request).company.id)
            new_milestone_set = []
            sales_cycles = []
            for milestone_data in data:
                try:
                    milestone = milestones.get(id=milestone_data.get('id', -1))
                except Milestone.DoesNotExist:
                    milestone = Milestone()
                else:
                    if milestone.title != milestone_data['title'] or \
                       milestone.color_code != milestone_data['color_code']:

                        for sales_cycle in milestone.sales_cycles.all():
                            sales_cycle.milestone = None
                            sales_cycle.save()
                            sales_cycles.append(sales_cycle)
                            meta = {"prev_milestone_color_code": milestone.color_code,
                                    "prev_milestone_title": milestone.title}
                            log_entry = SalesCycleLogEntry(sales_cycle=sales_cycle, 
                                                            owner=request.user.get_account(request).company,
                                                            entry_type=SalesCycleLogEntry.ME,
                                                            meta=json.dumps(meta))
                            log_entry.save()
                finally:
                    milestone.title = milestone_data['title']
                    milestone.color_code = milestone_data['color_code']
                    milestone.company_id = request.user.get_account(request).company.id
                    milestone.save()
                    new_milestone_set.append(milestone)

            for milestone in milestones:
                if milestone not in new_milestone_set:
                    for sales_cycle in milestone.sales_cycles.all():
                        sales_cycle.milestone = None
                        sales_cycle.save()
                        sales_cycles.append(sales_cycle)
                        meta = {"prev_milestone_color_code": milestone.color_code,
                                "prev_milestone_title": milestone.title}
                        log_entry = SalesCycleLogEntry(sales_cycle=sales_cycle, 
                                                        owner=request.user.get_account(request).company,
                                                        entry_type=SalesCycleLogEntry.MD,
                                                        meta=json.dumps(meta))
                        log_entry.save()
                    milestone.delete()
            bundle = {
                "milestones": [self.full_dehydrate(self.build_bundle(obj=milestone)) 
                                                            for milestone in new_milestone_set],
                "sales_cycles": [SalesCycleResource().full_dehydrate(SalesCycleResource().build_bundle(obj=sc)) 
                                                            for sc in sales_cycles]
            }

            if not self._meta.always_return_data:
                return http.HttpAccepted()
            else:
                return self.create_response(request, bundle,
                    response_class=http.HttpAccepted)


    def update(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post', 'get']):
            if request.method == "POST":
                request_data = self.deserialize(
                    request, request.body,
                    format=request.META.get('CONTENT_TYPE', 'application/json'))
                changed_milestones = []
                for data in request_data:
                    milestone = Milestone.objects.get(id=data['id'])
                    if milestone.sort != data['sort']:
                        try:
                            milestone_2 = Milestone.objects.get(company_id=data['company_id'], 
                                                            sort=data['sort'])
                        except MultipleObjectsReturned:
                            return http.HttpBadRequest()
                        temp = milestone.sort
                        milestone.sort = data['sort']
                        milestone_2.sort = temp
                        changed_milestones.append(milestone)
                        changed_milestones.append(milestone_2)

                for milestone in changed_milestones:
                    milestone.save()

            if not self._meta.always_return_data:
                return http.HttpAccepted()
            else:
                return self.create_response(request,
                    [MilestoneResource().get_bundle_detail(milestone, request) \
                    for milestone in Milestone.objects.filter(
                                        company_id=request.user.get_account(request).company.id
                                        )],
                    response_class=http.HttpAccepted)

class ActivityResource(CRMServiceModelResource):
    '''
    GET Method
    URL:  U{alma.net/api/v1/activity}\n
    Response:
    {
        "meta": {
        "limit": 20,
        "next": null,
        "offset": 0,
        "previous": null,
        "total_count": 1
        },
        "objects": [
            {
            "author_id": 1,
            "comments_count": 0,
            "date_created": "2015-05-14T12:16:39.363625",
            "date_finished": null,
            "deadline": null,
            "description": "Just trying to show an example of how to create activity",
            "has_read": false,
            "id": 1,
            "need_preparation": false,
            "resource_uri": "/api/v1/activity/1/",
            "sales_cycle_id": 1
            }
        ]
    }


    B{Description}:
    API resource to manage SalesCycle's Activities
    
    I{Create activity POST}\n
        B{accepts example} 
        C{
            author_id: 1
            comments_count: 0
            contact:{}
            author_id: 1
            children: []
            date_created: "2015-05-14T11:35:14.000637"
            id: 1
            owner: 1
            parent: null
            parent_id: null
            resource_uri: "/api/v1/contact/1/"
            sales_cycles: [1, 2]
            share: null
            status: 0
            company_id: 1
            tp: "user"
            vcard: {}
            date_created: "2015-05-14T12:16:39.363625"
            date_finished: null
            deadline: null
            description: "Just trying to show an example of how to create activity"
            has_read: false
            id: 1
            need_preparation: false
            resource_uri: "/api/v1/activity/1/"
            sales_cycle_id: "1"
            status: true
        }

    Response 
    {  
       "author_id":1,
       "comments_count":0,
       "contact":{},
       "date_created":"2015-05-14T12:16:39.363625",
       "date_finished":null,
       "deadline":null,
       "description":"Just trying to show an example of how to create activity",
       "has_read":false,
       "id":1,
       "need_preparation":false,
       "resource_uri":"/api/v1/activity/1/",
       "sales_cycle_id":"1",
       "status":true
    }

    I{Plan activity POST}\n
        B{accepts example} 
        C{
            author_id: 1
            comments_count: 0
            contact:{}
            author_id: 1
            children: []
            
            id: 1
            owner: 1
            parent: null
            parent_id: null
            resource_uri: "/api/v1/contact/1/"
            sales_cycles: [1, 2]
            share: null
            status: 0
            company_id: 1
            tp: "user"
            vcard: {}
            date_created: "2015-05-14T12:16:39.363625"
            date_finished: null
            deadline: "2015-06-01T00:00:00"
            description: "Just trying to show an example of how to plan activity"
            has_read: false
            id: 1
            need_preparation: false
            resource_uri: "/api/v1/activity/1/"
            sales_cycle_id: "1"
            status: true
        }

    Response 
    {  
       "author_id":1,
       "comments_count":0,
       "contact":{},
       "date_created":"2015-05-14T12:16:39.363625",
       "date_finished":null,
       "deadline":null,
       "description":"Just trying to show an example of how to create activity",
       "has_read":false,
       "id":1,
       "need_preparation":false,
       "resource_uri":"/api/v1/activity/1/",
       "sales_cycle_id":"1",
       "status":true
    }


    @undocumented: Meta

    
    '''

    author_id = fields.IntegerField(attribute='owner_id', null=True)
    assignee_id = fields.IntegerField(attribute='assignee_id', null=True)
    description = fields.CharField(attribute='description')
    need_preparation = fields.BooleanField(attribute='need_preparation')
    sales_cycle_id = fields.IntegerField(attribute='sales_cycle_id', null=True)
    comments_count = fields.IntegerField(attribute='comments_count', readonly=True)

    class Meta(CommonMeta):
        queryset = Activity.objects.all().select_related('owner').prefetch_related('comments', 'recipients')
        resource_name = 'activity'
        excludes = ['company_id', 'title']
        always_return_data = True
        filtering = {
            'author_id': ('exact', ),
            'owner': ALL_WITH_RELATIONS,
            'sales_cycle_id': ALL_WITH_RELATIONS
            }
        filtering.update(CommonMeta.filtering)

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/comments%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_comments'),
                name='api_get_comments'
            ),
            url(
                r"^(?P<resource_name>%s)/read%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('mark_as_read'),
                name='api_mark_as_ready'
            ),
            url(
                r"^(?P<resource_name>%s)/my_activities%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_my_activities'),
                name='api_my_activities'
            ),
            url(
                r"^(?P<resource_name>%s)/company_activities%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_account(request).company_activities'),
                name='api_company_activities'
            ),
            url(
                r"^(?P<resource_name>%s)/contact_activities/(?P<id>\d+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_contact_activities'),
                name='api_contact_activities'
            ),
            url(
                r"^(?P<resource_name>%s)/finish/(?P<id>\d+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('finish_activity'),
                name='api_finish_activity'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/move%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('move_activity'),
                name='api_move_activity'
            ),
        ]

    def dehydrate(self, bundle):
        bundle.data['has_read'] = self._has_read(bundle, bundle.request.user.id)

        # send updated contact (status was changed to LEAD)
        if bundle.data.get('obj_created'):
            if len(Contact.get_contact_activities(bundle.obj.contact.id)) == 1:
                bundle.data['contact'] = ContactResource().get_bundle_detail(bundle.obj.contact, bundle.request)
            bundle.data.pop('obj_created')
        # bundle.data['milestone_id'] = bundle.obj.milestone_id
        return bundle

    def _has_read(self, bundle, user_id):
        recip = None
        for r in bundle.obj.recipients.all():
            if r.user_id == user_id:
                recip = r
                break
        return not recip or recip.has_read

    # def hydrate_milestone(self, obj):
    #     return Milestone.objects.get(pk=bundle.data['milestone'])

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(self.__class__, self).build_filters(filters=filters)

        for k, v in filters.iteritems():
            if k.startswith('author_id'):
                orm_filters[k.replace('author_id', 'owner__id')] = v
                orm_filters.pop(k)
            if k == 'limit_for' and  v == 'mobile':
                orm_filters.update({'q': Activity.get_filter_for_mobile()})

        return orm_filters


    def get_comments(self, request, **kwargs):
        '''
        PUT, POST, GET METHODS
        I{URL}:  U{alma.net/api/v1/activity/:id/comments}

        Description:
        Api function to return comments of the activity
        @return:  comments

        >>> "objects": [
        ...     {
        ...         "comment": "Test comment 1",
        ...         "activity_id": 1,
        ...         "date_created": "2014-09-10T00:00:00",
        ...         "date_edited": "2014-12-29T09:45:24.166720",
        ...         "id": 1,
        ...         "resource_uri": "",
        ...         "company_id": 1
        ...         }
        ...     ]

        '''
        with RequestContext(self, request, allowed_methods=['post', 'get']):
            activity = Activity.objects.get(pk=kwargs.get('id'))
            comments = CommentResource().get_bundle_list(activity.comments.all(), request)
        return self.create_response(
            request, {'objects': comments})

    def mark_as_read(self, request, **kwargs):
        rv = 0
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            for act_id in data:
                Activity.mark_as_read(request.user.id, act_id)
            rv = len(data)
        return self.create_response(
            request, {'success': rv})

    def finish_activity(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            activity = Activity.objects.get(id=data.get('id'))
            activity.result = data.get('result')
            activity.date_finished = datetime.now(request.user.timezone)
            activity.save()
        return self.create_response(
            request, {
                'activity': ActivityResource().full_dehydrate(
                        ActivityResource().build_bundle(obj=activity, request=request) )})

    def move_activity(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
            if not data.get('sales_cycle_id', None):
                return http.HttpBadRequest()
            try:
                activity = Activity.objects.get(pk=kwargs.get('id'))
            except Activity.DoesNotExist:
                return http.HttpNotFound()

            try:
                sales_cycle = SalesCycle.objects.get(pk=data.get('sales_cycle_id', None))
            except SalesCycle.DoesNotExist:
                return http.HttpNotFound()

            objects = {}
            prev_sales_cycle = activity.sales_cycle
            activity.sales_cycle = sales_cycle
            activity.save()
            objects['prev_sales_cycle'] = SalesCycleResource().full_dehydrate(
                                            SalesCycleResource().build_bundle(
                                                obj=prev_sales_cycle, request=request))

            objects['activity'] = ActivityResource().full_dehydrate(
                                            ActivityResource().build_bundle(
                                                obj=activity, request=request))
            objects['next_sales_cycle'] =  SalesCycleResource().full_dehydrate(
                                            SalesCycleResource().build_bundle(
                                                obj=sales_cycle, request=request))

            return self.create_response(request, {'objects':objects}, response_class=http.HttpAccepted)

    def obj_create(self, bundle, **kwargs): ## TODO
        act = bundle.obj = self._meta.object_class()
        act.author_id = bundle.data.get('author_id')
        act.description = bundle.data.get('description')
        act.sales_cycle_id = bundle.data.get('sales_cycle_id')
        act.assignee_id = bundle.data.get('assignee_id')
        act.company_id = bundle.request.user.get_account(bundle.request).company.id
        if 'deadline' in bundle.data:
            act.deadline = bundle.data.get('deadline')
        if 'need_preparation' in bundle.data:
            act.need_preparation = bundle.data.get('need_preparation')
        act.save()
        text_parser(base_text=act.description, content_class=act.__class__,
                    object_id=act.id, company_id = bundle.request.user.get_account(bundle.request).company.id)
        act.spray(bundle.request.user.get_account(bundle.request).company.id)
        bundle = self.full_hydrate(bundle)

        bundle.data['obj_created'] = True
        return bundle

    def save(self, bundle, **kwargs):
        bundle = super(ActivityResource, self).save(bundle, **kwargs)
        if bundle.data.get('sales_cycle_id', None):
            new_sc_id = bundle.data.get('sales_cycle_id')
            if bundle.obj.sales_cycle_id != new_sc_id:
                sales_cycle = SalesCycle.objects.get(pk=new_sc_id)
                bundle.obj.sales_cycle = sales_cycle
                bundle.obj.save()
            if bundle.obj.company_id == None:
                bundle.obj.company_id = bundle.request.user.get_account(bundle.request).company.id
        bundle.obj.save()
        text_parser(base_text=bundle.obj.description, content_class=bundle.obj.__class__,
                    object_id=bundle.obj.id, company_id = bundle.request.user.get_account(bundle.request).company.id)
        return bundle


class ProductResource(CRMServiceModelResource):
    '''
    ALL+PATCH Method
    I{URL}:  U{alma.net/api/v1/product/}

    B{Description}:
    API resource to manage SalesCycle's Products


    @undocumented: Meta
    '''
    owner_id = fields.IntegerField(attribute='author_id', null=True)
#    sales_cycles = fields.ToManyField(SalesCycleResource, 'sales_cycles', readonly=True)

    class Meta(CommonMeta):
        queryset = Product.objects.all().prefetch_related('custom_field_values')
        resource_name = 'product'
        always_return_data = True

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/replace_cycles%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('replace_cycles'),
                name='api_replace_cycles'
            ),
            url(
                r"^(?P<resource_name>%s)/import%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('import_products'),
                name='api_import_products'
            ),
        ]

    def full_dehydrate(self, bundle, for_list=False):
        '''Custom representation of followers, assignees etc.'''
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=for_list)
        bundle.data['custom_fields'] = {}
        for field in bundle.obj.custom_field_values.all():
            bundle.data['custom_fields'][field.custom_field.id] = field.value
        return bundle

    def import_products(self, request, **kwargs):
        objects = []
        product_resource = ProductResource()
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        current_user = request.user
        decoded_string = base64.b64decode(data['uploaded_file'])
        file_extension = data['filename'].split('.')[1]
        if file_extension=='xls' or file_extension=='xlsx':
            for product in Product.import_from_xls(
                decoded_string, request.user, request.user.get_account(request).company.id):
                _bundle = product_resource.build_bundle(
                    obj=product, request=request)
                objects.append(product_resource.full_dehydrate(
                    _bundle, for_list=True))
        self.log_throttled_access(request)
        return self.create_response(request, {'objects': objects})

    def replace_cycles(self, request, **kwargs):
        '''
        PUT METHOD
        I{URL}:  U{alma.net/api/v1/product/:id/replace_cycles/}

        B{Description}:
        replace sales_cycles of the product
        @type  sales_cycle_ids: list
        @param sales_cycle_ids: sales_cycle_ids which should be set, for instace [1,2,3]

        @return: updated Product

        '''
        basic_bundle = self.build_bundle(request=request)
        # get sales_cycle
        try:
            obj = self.cached_obj_get(bundle=basic_bundle,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices(
                "More than one resource is found at this URI.")
        bundle = self.build_bundle(obj=obj, request=request)

        # get PUT's data from request.body
        deserialized = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)
        obj.sales_cycles.clear()
        obj.add_sales_cycles(deserialized['sales_cycle_ids'])
        obj_dict = {}
        obj_dict['success'] = obj
        return self.create_response(request, obj_dict, response_class=http.HttpAccepted)

    def save(self, bundle, **kwargs):
        bundle = super(self.__class__, self).save(bundle, **kwargs)
        if bundle.data.get('custom_fields', None):
            processing_custom_field_data(bundle.data['custom_fields'], bundle.obj)
        return bundle

class ProductGroupResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/product_group/}

    B{Description}:
    API resource to manage ProductGroup

    @undocumented: Meta
    '''
    products = fields.ListField(null=True)

    class Meta(CommonMeta):
        queryset = ProductGroup.objects.all()
        resource_name = 'product_group'
        always_return_data = True

    def dehydrate_products(self, bundle):
        return [product.pk for product in bundle.obj.products.all()]

    def hydrate_products(self, bundle):
        products = Product.objects.filter(pk__in=bundle.data['products'])
        bundle.data['products'] = products
        return bundle

    def obj_create(self, bundle, **kwargs):
        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        bundle = self.save(bundle)
        bundle.obj.products.add(*bundle.data['products'])
        return bundle

    def obj_update(self, bundle, **kwargs):
        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        bundle = self.save(bundle)
        bundle.obj.products.clear()
        bundle.obj.products.add(*bundle.data['products'])
        return bundle


class ValueResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/value/}

    B{Description}:
    API resource to manage SalesCycle's Value
    I{Note}: Model's 'amount' field was changed to 'value' in API

    @return: Value of SalesCycle

    >>> {
    ... "id": 1,
    ... "value": 20000
    ... "currency": "KZT",
    ... "resource_uri": "/api/v1/sales_cycle/value/1/",
    ... "salary": "monthly",
    ... "company_id": null,
    ... }

    @undocumented: Meta
    '''
    value = fields.IntegerField(attribute='amount')

    class Meta(CommonMeta):
        queryset = Value.objects.all()
        resource_name = 'sales_cycle/value'
        excludes = ['amount']


class ShareResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/share/}

    B{Description}:
    API resource to manage Shares of Contacts

    @undocumented: prepend_urls, Meta
    '''
    contact = fields.ToOneField(ContactResource, 'contact', full=False)
    share_to = fields.ToOneField(UserResource, 'share_to',
                                 full=False, null=True)
    share_from = fields.ToOneField(UserResource, 'share_from',
                                   full=False, null=True)

    class Meta(CommonMeta):
        queryset = Share.objects.all().select_related('contact', 'share_to', 'share_from')
        resource_name = 'share'
        excludes = ['company_id', 'description']

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/recent%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_shares'),
                name='api_last_shares'
            ),
            url(
                r"^(?P<resource_name>%s)/share_multiple%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('share_multiple'),
                name='api_share_multiple'
            ),
            url(
                r"^(?P<resource_name>%s)/read%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('read'),
                name='api_read'
            ),
        ]

    def get_last_shares(self, request, **kwargs):
        '''
        pass limit and offset  with GET request
        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        shares = Share.get_shares(self.request.user.id)
        return self.create_response(
            request,
            {'objects': self.get_bundle_list(shares, request)}
            )

    def share_multiple(self, request, **kwargs):
        '''
        Post example
        {
         "note": "sadasdasd",
          "contact": 10,
          "share_from": 1,
          "share_to":[1,2,3]
        }
        '''
        share_list = []
        deserialized = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        for json_obj in deserialized['shares']:
            s = Share(
                note=json_obj.get('note', ""),
                share_from=request.user,
                contact=Contact.objects.get(id=int(json_obj.get('contact'))),
                company_id=request.user.get_account(request).company.id,
                share_to=User.objects.get(id=int(json_obj.get('share_to')))
                )
            s.save()
            text_parser(base_text=s.note, content_class=s.__class__,
                    object_id=s.id, company_id = request.user.get_account(request).company.id)
            if s.share_to == request.user:
                share_list.append(s)

        return self.create_response(
            request, {
                'objects': self.get_bundle_list(share_list, request)
            })

    def read(self, request, **kwargs):
        '''
        POST example
        {'share_ids':[1,2,3]}
        '''
        share_list = []
        deserialized = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        share_ids = deserialized.get('share_ids')
        if share_ids and type(share_ids)==list:
            for share_id in share_ids:
                share = Share.objects.get(id=share_id)
                share.is_read = True
                share.save()
                share_list.append(share)
        return self.create_response(
            request,
            {
            'objects': self.get_bundle_list(share_list, request)}
            )

    def dehydrate_contact(self, bundle):
        return bundle.obj.contact_id

    def dehydrate_share_from(self, bundle):
        return bundle.obj.share_from_id

    def dehydrate_share_to(self, bundle):
        return bundle.obj.share_to_id

    def hydrate_contact(self, bundle):
        contact = Contact.objects.get(id=bundle.data['contact'])
        bundle.data['contact'] = contact
        return bundle

    def hydrate_share_from(self, bundle):
        share_from = User.objects.get(id=bundle.data['share_from'])
        bundle.data['share_from'] = share_from
        return bundle

    def hydrate_share_to(self, bundle):
        share_to = User.objects.get(id=bundle.data['share_to'])
        bundle.data['share_to'] = share_to
        return bundle

    def save(self, bundle, skip_errors=False):
        bundle = super(ShareResource, self).save(bundle)
        text_parser(base_text=bundle.obj.note, content_class=bundle.obj.__class__,
                    object_id=bundle.obj.id, company_id = bundle.request.user.get_account(bundle.request).company.id)
        return bundle


class CommentResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/comment/}

    B{Description}:
    API resource to manage Comments
    (GenericRelation with Activity, Contact, Share)

    @undocumented: Meta
    '''

    author_id = fields.IntegerField(attribute='owner_id')
    content_object = GenericForeignKeyField({
        Activity: ActivityResource,
        Contact: ContactResource,
        Share: ShareResource,
    }, 'content_object')

    class Meta(CommonMeta):
        queryset = Comment.objects.all()
        resource_name = 'comment'
        always_return_data = True

    def dehydrate(self, bundle):
        class_name = bundle.obj.content_object.__class__.__name__.lower()
        bundle.data[class_name+'_id'] = bundle.obj.content_object.id
        return bundle

    def hydrate(self, bundle):
        if bundle.data.get('id'):
            return bundle

        generics = ['activity_id', 'contact_id', 'share_id']
        model_name = filter(lambda k: k in generics, bundle.data.keys())[0]
        obj_class = ContentType.objects.get(app_label='alm_crm', model=model_name[:-3]).model_class()
        obj_id = bundle.data[model_name]
        bundle.data['object_id'] = obj_id
        bundle.data['company_id'] = bundle.request.user.get_account(bundle.request).company.id
        bundle.data['content_object'] = obj_class.objects.get(id=obj_id)
        bundle.data.pop(model_name)
        return bundle


    def save(self, bundle, skip_errors=False):
        bundle = super(CommentResource, self).save(bundle)
        text_parser(base_text=bundle.obj.comment, content_class=bundle.obj.__class__,
                    object_id=bundle.obj.id, company_id = bundle.request.user.get_account(bundle.request).company.id)
        return bundle


class MentionResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/comment/}

    B{Description}:
    API resource to manage Comments
    (GenericRelation with Contact, SalesCycle, Activity, Comment)

    @undocumented: Meta
    '''
    content_object = GenericForeignKeyField({
        Contact: ContactResource,
        SalesCycle: SalesCycleResource,
        Activity: ActivityResource,
        Comment: CommentResource,
    }, 'content_object')

    class Meta(CommonMeta):
        queryset = Mention.objects.all()
        resource_name = 'mention'


class ContactListResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/contact_list/}

    B{Description}:
    API resource to manage ContactList

    @undocumented: Meta
    '''
    contacts = fields.ListField(null=True)
    owner = fields.IntegerField(attribute='owner_id', readonly=True)

    class Meta(CommonMeta):
        queryset = ContactList.objects.all()
        resource_name = 'contact_list'
        always_return_data = True

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/contacts%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_contacts'),
                name='api_get_contacts'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/check_contact%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_contact'),
                name='api_check_contact'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/add_contacts%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('add_contacts'),
                name='api_add_contacts'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/delete_contact%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('delete_contact'),
                name='api_delete_contact'
            ),
        ]

    def dehydrate_contacts(self, bundle):
        return [contact.pk for contact in bundle.obj.contacts.all()]

    def hydrate_contacts(self, bundle):
        contacts = Contact.objects.filter(pk__in=bundle.data['contacts'])
        bundle.data['contacts'] = contacts
        return bundle

    def obj_create(self, bundle, **kwargs):
        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        bundle = self.save(bundle)
        bundle.obj.contacts.add(*bundle.data['contacts'])
        return bundle

    def save(self, bundle, **kwargs):
        bundle = super(self.__class__, self).save(bundle, **kwargs)
        if bundle.obj.id:
            bundle.obj.contacts.clear()
            bundle.obj.contacts.add(*bundle.data['contacts'])
        return bundle

    def post_list(self, request, **kwargs):
        '''
        POST METHOD
        I{URL}:  U{alma.net:8000/api/v1/contact_list/}

        Description:
        Api function for contact list creation. It creates contact list

        @return:  status 201

        >>> example POST payload
        ... {
        ...     title: "ALMA Cloud",
        ...     contacts: [
        ...         "/api/v1/crmuser/1/",
        ...         "/api/v1/crmuser/2/",
        ...     ]
        ... }
        '''
        return super(self.__class__, self).post_list(request, **kwargs)

    def delete_list(self, request, **kwargs):
        '''
        DELETE METHOD
        I{URL}:  U{alma.net:8000/api/v1/contact_list/:id/}

        Description:
        Api function for contact list creation. It creates contact list

        @return:  status 204

        >>> HTTP/1.0 204 NO CONTENT
        ... Date: Fri, 11 Nov 2014 06:48:36 GMT
        ... Server: WSGIServer/0.1 Python/2.7
        ... Content-Lenght: 0
        ... Content-Type:  text/html; charset=utf-8
        '''
        return super(self.__class__, self).delete_list(request, **kwargs)

    def put_detail(self, request, **kwargs):
        '''
        PATCH METHOD
        I{URL}:  U{alma.net:8000/api/v1/contact_list/:id/}

        Description:
        Api function for contact list creation. It creates contact list

        @return:  If a new resource is created status 201, if an existing resource is modified status 204,

        >>> HTTP/1.0 204 NO CONTENT
        ... Date: Fri, 11 Nov 2014 06:48:36 GMT
        ... Server: WSGIServer/0.1 Python/2.7
        ... Content-Lenght: 0
        ... Content-Type:  text/html; charset=utf-8
        '''
        return super(self.__class__, self).put_detail(request, **kwargs)

    def get_contacts(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/contacts}

        Description:
        Api function to return the contact list contacts

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default
        @return:  contacts

        >>> "objects": [
        ...     {
        ...         "id": 1,
        ...         "resource_uri": "/api/v1/contact_list/1/",
        ...         "company_id": null,
        ...         "title": "ALMA Cloud",
        ...         "contacts": [
        ...         {
        ...             "id": 1,
        ...             "is_supervisor": false,
        ...             "organization_id": 1,
        ...             "resource_uri": "/api/v1/crmuser/1/",
        ...             "company_id": 1,
        ...             "user_id": 1
        ...         },
        ...         {
        ...             "id": 2,
        ...             "is_supervisor": false,
        ...             "organization_id": 1,
        ...             "resource_uri": "/api/v1/crmuser/2/",
        ...             "company_id": 1,
        ...             "user_id": 2
        ...         }
        ...     ]

        '''
        try:
            contact_list = ContactList.objects.get(id=kwargs.get('id'))
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            contacts = contact_list.contacts.all()[offset:offset + limit]
            crm_user_resource = ContactResource()
            obj_dict = {}
            obj_dict['objects'] = \
                crm_user_resource.get_bundle_list(contacts, request)
            return self.create_response(request, obj_dict)
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )

    def check_contact(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/check_contact}

        Description:
        Api function to return existence contact in the contact list

        @type  contact_id: number
        @param contact_id: contact id which you are checking.

        @return:  success and list of boolean fields

        >>> {
        ...    "success": true
        ... }

        '''
        try:
            contact_list = ContactList.objects.get(id=kwargs.get('id'))
            contact_id = int(request.GET.get('contact_id', 0))
            if not contact_id:
                return self.create_response(
                    request,
                    {'success': False, 'error_string': 'contact id is not set'}
                    )
            return self.create_response(
                request,
                {'success': ContactList.objects.get(id=kwargs.get('id')).check_contact(contact_id=contact_id)}
                )
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )

    def add_contacts(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/add_contacts}

        Description:
        Api function to add contacts to the contact list

        @type  user_ids: list
        @param user_ids: Adding user ids for adding.

        @return:  success and list of boolean fields

        >>> {
        ...    "success": [True, False, False, True]
        ... }

        '''
        try:
            contact_ids = ast.literal_eval(request.GET.get('contact_ids'))
            if not contact_ids:
                return self.create_response(
                    request,
                    {'success': False, 'error_string': 'Contact ids is not set'}
                    )
            obj_dict = {}
            obj_dict['success'] = ContactList.objects.get(id=kwargs.get('id')).add_contacts(contact_ids=contact_ids)
            return self.create_response(
                request, obj_dict)
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )

    def delete_contact(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/delete_user}

        Description:
        Api function to delete a user in the contact list

        @type  user_id: number
        @param user_id: User id which you are checking.

        @return:  success delated or not

        >>> {
        ...    "success": true
        ... }

        '''
        try:
            contact_list = ContactList.objects.get(id=kwargs.get('id'))
            contact_id = int(request.GET.get('contact_id', 0))
            if not contact_id:
                return self.create_response(
                    request,
                    {'success': False, 'error_string': 'Contact id is not set'}
                    )
            return self.create_response(
                request,
                {'success':
                    ContactList.objects.get(id=kwargs.get('id')).delete_contact(
                        contact_id=contact_id)}
                )
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )


class ConstantsObject(object):
    '''
    @undocumented: __init__
    '''

    def __init__(self, service_slug=None, bundle=None):
        if service_slug is None:
            return
        # request = bundle.request

        self.data = {
            'sales_cycle': {
                'statuses': SalesCycle.STATUSES_OPTIONS,
                'statuses_hash': SalesCycle.STATUSES_DICT
            },
            'sales_cycle_log_entry': {
                'types_hash': SalesCycleLogEntry.TYPES_DICT
            },
            'contact': {
                'statuses': Contact.STATUSES_OPTIONS,
                'statuses_hash': Contact.STATUSES_DICT,
                'tp': Contact.TYPES_OPTIONS,
                'tp_hash': Contact.TYPES_DICT
            },
            'vcard': {
                'email': {'types': Email.TYPE_CHOICES},
                'adr': {'types': Adr.TYPE_CHOICES},
                'phone': {'types': Tel.TYPE_CHOICES}
            }
        }

    def to_dict(self):
        return self.data



class ConstantsResource(Resource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/constants/}

    B{Description}:
    API resource to get all data of application initial state:
    objects(users, contacts, activities, etc.), constants and session data

    @undocumented: Meta
    '''
    # objects = fields.DictField(attribute='objects', readonly=True)
    # # constants = fields.DictField(attribute='constants', readonly=True)
    # # session = fields.DictField(attribute='session', readonly=True)

    class Meta:
        resource_name = 'constants'
        authorization = Authorization()

    def get_detail(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        constants = self.obj_get(bundle=base_bundle, **kwargs)
        return self.create_response(request, {"constants": constants.to_dict()})

    def obj_get(self, bundle, **kwargs):
        return ConstantsObject(service_slug=DEFAULT_SERVICE, bundle=bundle)


class AppStateObject(object):
    '''
    @undocumented: __init__, get_users, get_account(request).company, get_contacts,
    get_sales_cycles, get_activities, get_shares, get_constants,
    get_session
    '''

    def __init__(self, service_slug=None, request=None):
        if service_slug is None:
            return
        self.request = request
        self.service_slug = service_slug
        self.company = request.company

        self.constants = self.get_constants()
        self.categories = self.get_categories()

    def get_categories(self):
        return [x.data for x in Category.objects.filter(vcard__contact__company_id=self.company.id)]

    def get_constants(self):
        return {
            'sales_cycle': {
                'statuses': SalesCycle.STATUSES_OPTIONS,
                'statuses_hash': SalesCycle.STATUSES_DICT
            },
            'sales_cycle_log_entry': {
                'types_hash': SalesCycleLogEntry.TYPES_DICT
            },
            'contact': {
                'statuses': Contact.STATUSES_OPTIONS,
                'statuses_hash': Contact.STATUSES_DICT,
                'tp': Contact.TYPES_OPTIONS,
                'tp_hash': Contact.TYPES_DICT
            },
            'vcard': {
                'email': {'types': Email.TYPE_CHOICES},
                'adr': {'types': Adr.TYPE_CHOICES},
                'tel': {'types': Tel.TYPE_CHOICES},
                'url': {'types': Url.TYPE_CHOICES}
            }
        }

    def to_dict(self):
        return self._data


class AppStateResource(Resource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/app_state/}

    B{Description}:
    API resource to get all data of application initial state:
    objects(users, contacts, activities, etc.), constants and session data

    @undocumented: Meta
    '''
    categories = fields.ListField(attribute='categories', readonly=True)
    constants = fields.DictField(attribute='constants', readonly=True)

    class Meta:
        resource_name = 'app_state'
        # object_class = AppStateObject
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/my_feed%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('my_feed'),
                name='api_my_feed'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<slug>\w+)/categories%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_categories'),
                name='api_get_categories'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<slug>\w+)/company%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_account(request).company'),
                name='api_get_account(request).company'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<slug>\w+)/constants%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_constants'),
                name='api_get_constants'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<slug>\w+)/session%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_session'),
                name='api_get_session'
            ),
        ]

    def obj_get(self, bundle, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/app_state/:service_slug/}

        B{Description}:
        API function to get application's initial data

        @type  service_slug: string
        @param service_slug: Service's slug name.

        @return: dict of objects, contacts and session data

        >>> {
        ... 'session': {
        ...     'logged_in': True,
        ...     'session_key': '0pp2uy626ochy0kz0remjl29tbdc8b15',
        ...     'user_id': 1,
        ...     'language': 'en-us'
        ...     },
        ... 'objects': {
        ...     'activities': [{
        ...         'id': 5,
        ...         'date_created':
        ...         '2014-09-15 00:00',
        ...         'author_id': 1,
        ...         'description': 'd5',
        ...     }],
        ...     'users': [{
        ...         'first_name': 'Bruce',
        ...         'last_name': 'Wayne',
        ...         'company_id': 1,
        ...         'email': 'b.wayne@batman.bat',
        ...         'is_admin': False,
        ...         'id': 1
        ...         }],
        ...     'contacts': [{
        ...         'status': 1,
        ...         'tp': 'user',
        ...         'vcard': {
        ...             'org': {'id': None, 'value': None},
        ...             'adrs': [],
        ...             'emails': [{'type': 'WORK', 'id': 1, 'value': 'akerke.akerke@gmail.com'}],
        ...             'urls': [],
        ...             'phones': [{'type': 'CELL', 'id': 1, 'value': '87753591453'}]
        ...             },
        ...         'parent_id': 1,
        ...         'date_created':
        ...         '2014-09-10 00:00',
        ...         'id': 1,
        ...         'owner_id': 1
        ...         }],
        ...     'company': [{
        ...         'subdomain': 'almacloud',
        ...         'owner_id': 1,
        ...         'id': 1,
        ...         'name': 'ALMACloud'
        ...         }],
        ...     'shares': [],
        ...     'sales_cycles': [{
        ...         'status': 'N',
        ...         'description': None,
        ...         'title': '',
        ...         'real_value': {'id': 3, 'value': 100000},
        ...         'projected_value': {'id': 3, 'value': 100000},
        ...         'contact_id': 1,
        ...         'product_ids': '[]',
        ...         'date_created': '2014-09-12 00:00',
        ...         'id': 3,
        ...         'owner_id': 1
        ...         }]
        ...     },
        ... 'constants': {
        ...     'vcard__adr': {
        ...         'types': [{'INTL': 'INTL'}, {'POSTAL': 'postal'},
        ...             {'PARCEL': 'parcel'}, {u'WORK': u'work'}, {u'dom': u'dom'},
        ...             {u'home': u'home'}, {u'pref': u'pref'}
        ...             ]
        ...         },
        ...     'vcard__phone': {
        ...         'types': [{'VOICE': 'INTL'}, {'HOME': 'home'},
        ...             {'MSG': 'message'}, {'WORK': 'work'}, {'pref': 'prefered'},
        ...             {'fax': 'fax'}, {'cell': 'cell phone'}, {'video': 'video'},
        ...             {'pager': 'pager'}, {'bbs': 'bbs'}, {'modem': 'modem'},
        ...             {'car': 'car phone'}, {'isdn': 'isdn'}, {'pcs': 'pcs'}
        ...             ]
        ...         },
        ...     'contacts': {
        ...         'tp': [{'co': 'company type'}, {'user': 'user type'}],
        ...         'statuses': [{'0': 'new_contact'}, {'1': 'lead_contact'},
        ...             {'2': u'opportunity_contact'}, {'3': 'client_contact'}]
        ...     },
        ...     'vcard__email': {'types': [{'INTERNET': 'internet'}, {'x400': 'x400'}, {'pref': 'pref'}]},
        ...     'salescycle': {'statuses': [{'N': 'New'}, {'P': 'Pending'}, {'C': 'Completed'}]}
        ...     },
        ... 'resource_uri': ''
        ... }

        '''

        return AppStateObject(service_slug=kwargs['pk'], request=bundle.request)

    def my_feed(self, request, **kwargs):
        '''
        pass limit and offset with GET request
        '''
        activities, sales_cycles, s2a_map = \
            Activity.get_activities_by_date_created(request.user.get_account(request).company.id,
                                                    owned=True, mentioned=True,
                                                    include_sales_cycles=True)

        return self.create_response(
            request,
            {
                'sales_cycles': SalesCycleResource().get_bundle_list(sales_cycles, request),
                'activities': ActivityResource().get_bundle_list(activities, request)
            })

    def get_categories(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            obj = AppStateObject(service_slug=kwargs['slug'], request=request)
            return self.create_response(request, {'objects': obj.get_categories()}, response_class=http.HttpAccepted)

    def get_company(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            obj = AppStateObject(service_slug=kwargs['slug'], request=request)
            return self.create_response(request, {'objects': obj.get_account(request).company()}, response_class=http.HttpAccepted)

    def get_constants(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            obj = AppStateObject(service_slug=kwargs['slug'], request=request)
            return self.create_response(request, {'objects': obj.get_constants()}, response_class=http.HttpAccepted)

    def get_session(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            obj = AppStateObject(service_slug=kwargs['slug'], request=request)
            return self.create_response(request, {'objects': obj.get_session()}, response_class=http.HttpAccepted)


class MobileStateObject(object):
    '''
    @undocumented: __init__, get_users, get_account(request).company, get_contacts,
    get_sales_cycles, get_activities, get_shares, get_constants,
    get_session
    '''

    def __init__(self, service_slug=None, bundle=None):
        if service_slug is None:
            return
        request = bundle.request
        self.request = request
        self.current_user = request.user
        self.company_id = request.user.get_account(request).company.id
        self.company = request.user.get_account(request).company()
        self.current_user = request.account

        sales_cycles = SalesCycleResource().obj_get_list(bundle, limit_for='mobile')

        sc_ids_param = ','.join([str(sc.id) for sc in sales_cycles])
        activities = ActivityResource().obj_get_list(bundle, limit_for='mobile',
            sales_cycle_id__in=sc_ids_param)

        contact_ids_param = ','.join(set([str(sc.contact_id) for sc in sales_cycles]))
        contacts = ContactResource().obj_get_list(bundle, id__in=contact_ids_param)

        cu_ids = set([str(a.owner_id) for a in activities])
        cu_ids = cu_ids.union([str(sc.owner_id) for sc in sales_cycles])
        cu_ids_param = ','.join(cu_ids)
        users = UserResource().obj_get_list(bundle, id__in=cu_ids_param)

        milestones = MilestoneResource().obj_get_list(bundle)

        self.resources = {
            'sales_cycles': SalesCycleResource,
            'activities': ActivityResource,
            'contacts': ContactResource,
            'users': UserResource,
            'milestones': MilestoneResource
        }

        self.objects = {
            'sales_cycles': sales_cycles,
            'activities': activities,
            'contacts': contacts,
            'users': users,
            'milestones': milestones
        }


class MobileStateResource(Resource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/mobile_state/}

    B{Description}:
    API resource to get all data of application initial state:
    objects(users, contacts, activities, etc.), constants and session data

    @undocumented: Meta
    '''
    # objects = fields.DictField(attribute='objects', readonly=True)
    # # constants = fields.DictField(attribute='constants', readonly=True)
    # # session = fields.DictField(attribute='session', readonly=True)

    class Meta:
        resource_name = 'mobile_state'
        authorization = Authorization()

    def get_detail(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        mobile_state = self.obj_get(bundle=base_bundle, **kwargs)

        serialized = {
            'objects': {},
            'constants': ConstantsObject(service_slug=DEFAULT_SERVICE).to_dict(),
            'timestamp': datetime.now(pytz.timezone(settings.TIME_ZONE)).__str__()
        }
        for resource_name, objects in mobile_state.objects.iteritems():
            bundles = []
            ResourceInstance = mobile_state.resources[resource_name]()
            for obj in objects:
                bundle = self.build_bundle(obj=obj, request=request)
                setattr(bundle, 'skip_fields', ['activities'])
                setattr(bundle, 'use_fields', ['activities_count'])
                bundles.append(ResourceInstance.full_dehydrate(bundle, for_list=True))
            serialized['objects'][resource_name] = bundles

        return self.create_response(request, serialized)

    def obj_get(self, bundle, **kwargs):
        return MobileStateObject(service_slug=DEFAULT_SERVICE, bundle=bundle)


class SalesCycleProductStatResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/cycle_product_stat/}

    B{Description}:
    API resource to manage SalesCycleProductStatResource

    @undocumented: Meta
    '''
    product_id = fields.ToOneField(
        'alm_crm.api.ProductResource', 'product', null=False, full=False)
    sales_cycle = fields.ToOneField(
        'alm_crm.api.SalesCycleResource', 'sales_cycle', null=False, full=False)

    class Meta(CommonMeta):
        queryset = SalesCycleProductStat.objects.all()
        resource_name = 'cycle_product_stat'

    def dehydrate_product_id(self, bundle):
        return bundle.obj.product.id

    def hydrate_product_id(self, bundle):
        product = Product.objects.get(id=bundle.data['product_id'])
        bundle.data['product_id'] = product
        return bundle

    def dehydrate_sales_cycle(self, bundle):
        return bundle.obj.product_id

    def hydrate_sales_cycle(self, bundle):
        sales_cycle = SalesCycle.objects.get(id=bundle.data['sales_cycle'])
        bundle.data['sales_cycle'] = sales_cycle
        return bundle


class FilterResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/filter/}

    B{Description}:
    API resource to manage Filter

    @undocumented: Meta
    '''
    author_id = fields.IntegerField(attribute='owner_id')

    class Meta(CommonMeta):
        queryset = Filter.objects.all()
        resource_name = 'filter'
        always_return_data = True


class HashTagReferenceResource(CRMServiceModelResource):

    content_object = GenericForeignKeyField({
        Activity: ActivityResource,
        Share: ShareResource,
        Comment: CommentResource,
    }, 'content_object')

    class Meta(CommonMeta):
        queryset = HashTagReference.objects.all()
        resource_name = 'hashtag_reference'


    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/search/(?P<pattern>\w+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('search'),
                name='api_search'
            )]

    def search(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/hashtag_reference/search/:hashtag/}

        Description:
        Api function to return Objects related with giver hashtag

        @type  hashtag: string
        @param hashtag: hashtag format string.

        @return:  objects

        >>> {
        ...    "objects": {
        ...        "activities":[],
        ...        "contacts": [],
        ...        "comments": [],
        ...        "sales_cycles": []}
        ... }

        '''
        try:
            if not kwargs.get('pattern', None):
                return http.HttpBadRequest()

            hashtag = HashTag.objects.get(text='#'+kwargs.get('pattern', None))
            activities = []
            shares = []
            comments = []
            sales_cycles = []
            for reference in hashtag.references.all():
                if isinstance(reference.content_object, Activity):
                    activities.append(reference.content_object)
                    if reference.content_object.sales_cycle not in sales_cycles:
                        sales_cycles.append(reference.content_object.sales_cycle)
                elif isinstance(reference.content_object, Share):
                    shares.append(reference.content_object)
                elif isinstance(reference.content_object, Comment):
                    comments.append(reference.content_object)

            obj_dict = {'objects':{}}
            if activities:
                activity_resource = ActivityResource()
                obj_dict['objects']['activities'] = \
                    activity_resource.get_bundle_list(activities, request)

            if shares:
                share_resource = ShareResource()
                shares_list = []
                for share in shares:
                    if share.share_to == request.user:
                        shares_list.append(share)

                obj_dict['objects']['shares'] = \
                    share_resource.get_bundle_list(shares_list, request)

            if comments:
                comment_resource = CommentResource()
                obj_dict['objects']['comments'] = \
                    comment_resource.get_bundle_list(comments, request)

            if sales_cycles:
                salescycle_resource = SalesCycleResource()
                obj_dict['objects']['sales_cycles'] = \
                    salescycle_resource.get_bundle_list(sales_cycles, request)
            return self.create_response(request, obj_dict, response_class=http.HttpAccepted)
        except HashTag.DoesNotExist:
            return http.HttpNotFound()


class CustomSectionResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/custom_section/}
    B{Description}:
    API resource to manage CustomSection
    (GenericRelation with VCard, Product)
    @undocumented: Meta
    '''
    # field_values = fields.ToManyField('alm_crm.api.CustomFieldValueResource', 'field_values',
    #                            related_name='product', null=True,
    #                            full=True, readonly=True)

    content_object = GenericForeignKeyField({
        Product: ProductResource,
        VCard: VCardResource,
    }, 'content_object')

    class Meta(CommonMeta):
        queryset = CustomSection.objects.all()
        resource_name = 'custom_section'

class CustomFieldResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/custom_field/}
    B{Description}:
    API resource to manage CustomFields
    (GenericRelation with VCard, Product)
    @undocumented: Meta
    '''

    content_type = fields.CharField()

    class Meta(CommonMeta):
        queryset = CustomField.objects.all()
        resource_name = 'custom_field'

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/bulk_edit%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('bulk_edit'),
                name='api_bulk_edit'
            ),
            url(
                r"^(?P<resource_name>%s)/get_for_model/(?P<class>\w+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_for_model'),
                name='api_get_for_model'
            )
        ]

    # def full_dehydrate(self, bundle, for_list=False):
    #     '''Custom representation of followers, assignees etc.'''
    #     bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=for_list)
    #     bundle.data['content_type'] = bundle.obj.content_type
    #     return bundle

    def bulk_edit(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))

            fields_set = []       
            content_class = data['content_class']
            changed_objects = []

            for object in data['custom_fields']:
                try:
                    field = CustomField.objects.get(id=object.get('id', -1))
                except CustomField.DoesNotExist:
                    field = CustomField()
                finally:
                    field.title = object['title']
                    field.content_type = ContentType.objects.get(app_label="alm_crm", model=content_class)
                    field.company_id = request.user.get_account(request).company.id
                    field.save()
                    fields_set.append(field)

            for field in CustomField.objects.filter(company_id=request.user.get_account(request).company.id,
                                                    content_type=ContentType.objects.get(app_label="alm_crm", model=content_class)):
                if field not in fields_set:
                    if field.values.all().count() != 0:
                        for field_value in field.values.all():
                            if content_class.lower() == "contact":
                                if field_value.content_object not in changed_objects:
                                    vcard_note = Note(vcard=field_value.content_object.vcard, data='')
                                else:
                                    vcard_note = field_value.content_object.vcard.note_set.last()
                                vcard_note.data += field.title+': '+field_value.value+'\n'
                                vcard_note.save()
                            changed_objects.append(field_value.content_object)
                            field_value.delete()
                    field.delete()

            changed_objects_bundle = []

            if content_class.lower() == "product":
                changed_objects_bundle = [ProductResource().full_dehydrate(ProductResource().build_bundle(obj=obj)) for obj in changed_objects]
            elif content_class.lower() == "contact":
                changed_objects_bundle = [ContactResource().full_dehydrate(ContactResource().build_bundle(obj=obj)) for obj in changed_objects]

            bundle = {'content_class': content_class,
                        'custom_fields': [self.full_dehydrate(self.build_bundle(obj=field)) for field in fields_set],
                        'changed_objects': changed_objects_bundle}

            return self.create_response(request, 
                        bundle, 
                        response_class=http.HttpAccepted)

    def get_for_model(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            try:
                content_type = ContentType.objects.get(app_label='alm_crm', model=kwargs.get("class", ""))
            except ContentType.DoesNotExist:
                return http.HttpNotFound()
            else:
                objects = CustomField.objects.filter(company_id=request.account.company.id,
                                                    content_type=content_type)

                return self.create_response(request, 
                        [self.full_dehydrate(self.build_bundle(obj=obj)) for obj in objects], 
                        response_class=http.HttpAccepted)
           

class CustomFieldValueResource(CRMServiceModelResource):

    content_object = GenericForeignKeyField({
        Product: ProductResource,
        Contact: ContactResource,
    }, 'content_object')

    custom_field = fields.ToOneField('alm_crm.api.CustomFieldResource', 'custom_field',
        null=True, full=True)

    class Meta(CommonMeta):
        queryset = CustomFieldValue.objects.all()
        resource_name = 'field_value'

class ReportResource(Resource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/reports/}

    B{Description}:
    API resource to get data for reports

    @undocumented: Meta
    '''

    class Meta:
        resource_name = 'reports'
        object_class = AppStateObject
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/funnel%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('funnel'),
                name='api_funnel'
            ),
            url(
                r"^(?P<resource_name>%s)/realtime_funnel%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('realtime_funnel'),
                name='api_realtime_funnel'
            ),
            url(
                r"^(?P<resource_name>%s)/user_report%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('user_report'),
                name='api_user_report'
            ),
            url(
                r"^(?P<resource_name>%s)/product_report%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('product_report'),
                name='api_product_report'
            )]

    def funnel(self, request, **kwargs):
        '''
        retrieves data for building sales funnel
        '''
        if request.body:
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
        else:
            data = {}
        return self.create_response(
            request,
            report_builders.build_funnel(request.company.id, data))

    def realtime_funnel(self, request, **kwargs):
        '''
        retrieves data for building sales funnel
        '''
        if request.body:
            data = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
        else:
            data = {}

        return self.create_response(
            request,
            report_builders.build_realtime_funnel(request.user.get_account(request).company.id, data))


    def user_report(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):

            if request.body:
                data = self.deserialize(
                    request, request.body,
                    format=request.META.get('CONTENT_TYPE', 'application/json')) if request.body else {}
            else:
                data = {}
            return self.create_response(
                request, report_builders.build_user_report(
                    company_id=request.user.get_account(request).company.id,
                    data=data), response_class=http.HttpAccepted
                )
        

    def product_report(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            if request.body:
                data = self.deserialize(
                    request, request.body,
                    format=request.META.get('CONTENT_TYPE', 'application/json')) if request.body else {}
            else:
                data = {}
            return self.create_response(
                request, report_builders.build_product_report(
                    company_id=request.user.get_account(request).company.id,
                    data=data), response_class=http.HttpAccepted
                )
