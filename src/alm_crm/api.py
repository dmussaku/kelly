from .models import (
    SalesCycle,
    Product,
    Activity,
    Contact,
    ContactList,
    Share,
    CRMUser,
    Value,
    Feedback,
    Comment,
    Mention,
    SalesCycleProductStat,
    Filter
    )
from alm_vcard.api import VCardResource
from alm_vcard.models import *
from almanet.settings import DEFAULT_SERVICE
from almanet.utils.api import RequestContext
from almanet.utils.env import get_subscr_id
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.utils import translation
from tastypie import fields, http
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.exceptions import ImmediateHttpResponse, NotFound, Unauthorized
from tastypie.resources import Resource, ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
import ast
import datetime
import time


class CommonMeta:
    list_allowed_methods = ['get', 'post', 'patch']
    detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
    authentication = MultiAuthentication(SessionAuthentication(),
                                         BasicAuthentication())
    authorization = Authorization()


class CRMServiceModelResource(ModelResource):

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(subscription_id=self.get_crmsubscr_id(request))

    def hydrate(self, bundle):
        """
        bundle.request.user_env is empty dict{}
        because bundle.request.user is AnonymousUser
        it happen when tastypie uses BasicAuthentication or another
        which doesn't have session
        """
        crmuser = self.get_crmuser(bundle.request)
        if crmuser:
            bundle.obj.owner = crmuser

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

    @classmethod
    def get_crmsubscr_id(cls, request):
        return get_subscr_id(request.user_env, DEFAULT_SERVICE)

    @classmethod
    def get_crmuser(cls, request):
        subscription_pk = cls.get_crmsubscr_id(request)
        crmuser = None
        if subscription_pk:
            crmuser = request.user.get_subscr_user(subscription_pk)
        return crmuser

    class Meta:
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        authentication = MultiAuthentication(SessionAuthentication(),
                                             BasicAuthentication())
        authorization = Authorization()


class ContactResource(CRMServiceModelResource):
    """
    GET Method
    I{URL}:  U{alma.net/api/v1/contact}

    Description
    Api for Contact model


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
    ...     "subscription_id": 1,
    ...     "tp": "user",
    ...     "vcard": {...}
    ... },


    @undocumented: prepend_urls, Meta
    """
    vcard = fields.ToOneField('alm_vcard.api.VCardResource', 'vcard',
                              null=True, full=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'owner',
                              null=True, full=False)
    # followers = fields.ToManyField('alm_crm.api.CRMUserResource', 'followers',
    #                                null=True, full=False)
    # assignees = fields.ToManyField('alm_crm.api.CRMUserResource', 'assignees',
    #                                null=True, full=False)
    sales_cycles = fields.ToManyField(
        'alm_crm.api.SalesCycleResource', 'sales_cycles',
        related_name='contact', null=True, full=False)
    parent = fields.ToOneField(
        'alm_crm.api.ContactResource', 'parent',
        null=True, full=False
        )
    # shares = fields.ToManyField(
    #     'alm_crm.api.ShareResource', 'shares',
    #     null=True, full=True
    #     )

    class Meta(CommonMeta):
        queryset = Contact.objects.all()
        resource_name = 'contact'
        filtering = {
            'status': ['exact'],
            'tp': ['exact']
        }

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
        bundle = super(self.__class__, self).full_dehydrate(
            bundle, for_list=True)
        bundle.data['share'] = self.serialize_share(ShareResource, bundle.obj.share_set.first())
        bundle.data['children'] = [contact.id for contact in bundle.obj.children.all()]
        bundle.data['author_id'] = bundle.obj.owner_id
        bundle.data['parent_id'] = bundle.obj.parent_id
        return bundle

    # def dehydrate_assignees(self, bundle):
    #     return [assignee.pk for assignee in bundle.obj.assignees.all()]

    # def dehydrate_followers(self, bundle):
    #     return [follower.pk for follower in bundle.obj.followers.all()]
    def serialize_share(self, resource, obj):
        if not obj:
            return None
        return resource().full_dehydrate(
                    resource().build_bundle(
                        obj=obj)
                    )

    # def dehydrate_shares(self, bundle):
    #     return [self.serialize_share(ShareResource, share) for share in bundle.obj.share_set.all()]

    def dehydrate_sales_cycles(self, bundle):
        return [sc.pk for sc in bundle.obj.sales_cycles.all()]

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
        contact_id = kwargs.get('pk', None)
        subscription_id = self.get_crmsubscr_id(bundle.request)
        if contact_id:
            bundle.obj = Contact.objects.get(id=int(contact_id))
            bundle.obj.subscription_id = subscription_id
        else:
            bundle.obj = self._meta.object_class()
            bundle.obj.subscription_id = subscription_id
            bundle.obj.owner_id = bundle.request.user.get_crmuser().id
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
        field_names.remove('share')
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
                        print vcard_bundle
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
                bundle.obj.create_share_to(self.get_crmuser(bundle.request).id,
                                           bundle.data.get('note'))
            if not kwargs.get('pk'):
                SalesCycle.create_globalcycle(
                    **{'subscription_id':subscription_id,
                     'owner_id':self.get_crmuser(bundle.request).id,
                     'contact_id':bundle.obj.id
                    }
                )
        # t4=time.time()-t3
        # print "Time to finish creating share and sales_cycle objects %s" % t4
        return bundle

    def follow_contacts(self, request, **kwargs):
        if kwargs.get('contact_ids'):
            try:
                contact_ids = ast.literal_eval(
                    kwargs.get('contact_ids'))
            except:
                return self.create_response(
                    request, {'success':False, 'message':'Pass a list as a parameter'}
                    )
        crmuser = request.user.get_crmuser()
        for contact_id in contact_ids:
            try:
                crmuser.unfollow_list.remove(
                    Contact.objects.get(id=contact_id))
            except DoesNotExist:
                return self.create_response(
                    request, {'success':False, 'message':'Contact with a given id does not exist'}
                    )
        crmuser.save()
        return self.create_response(
                    request, {'success':True, 'message':'You successfully followed %s' % contact}
                    )

    def unfollow_contacts(self, request, **kwargs):
        if kwargs.get('contact_ids'):
            try:
                contact_ids = ast.literal_eval(
                    kwargs.get('contact_ids'))
            except:
                return self.create_response(
                    request, {'success':False, 'message':'Pass a list as a parameter'}
                    )
        crmuser = request.user.get_crmuser()
        for contact_id in contact_ids:
            try:
                crmuser.unfollow_list.add(
                    Contact.objects.get(id=contact_id))
            except DoesNotExist:
                return self.create_response(
                    request, {'success':False, 'message':'Contact with a given id does not exist'}
                    )
        crmuser.save()
        return self.create_response(
                    request, {'success':True, 'message':'You successfully followed %s' % contact}
                    )

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
        ...     "subscription_id": 1,
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
            subscription_id = request.user.get_crmuser().subscription_id,
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
        ... "subscription_id": 1,
        ... "tp": "user",
        ... "vcard": {...}
        ... },
        ... ]

        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        contacts = Contact.get_cold_base(self.get_crmsubscr_id(request))
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
        ...     "subscription_id": 1,
        ...     "tp": "user",
        ...     "vcard": {...}
        ... },
        ... ]

        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        contacts = Contact.get_contacts_by_status(self.get_crmsubscr_id(request),
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
        ...     "subscription_id": null
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
        ...     "feedback": null,
        ...     "id": 30,
        ...     "owner": null,
        ...     "resource_uri": "/api/v1/activity/30/",
        ...     "sales_cycle": "/api/v1/sales_cycle/3/",
        ...     "subscription_id": null,
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
        ...     "subscription_id": null,
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
            subscription_id=self.get_crmsubscr_id(request),
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
        return self.create_response(
            request,
            {'success':
                Contact.share_contact(share_from, share_to, contact_id)}
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

        current_crmuser = request.user.get_crmuser()
        for contact in Contact.import_from_vcard(
                data['uploaded_file'], current_crmuser):

            contact.create_share_to(current_crmuser.pk)

            _bundle = contact_resource.build_bundle(
                obj=contact, request=request)
            objects.append(contact_resource.full_dehydrate(
                _bundle, for_list=True))
        self.log_throttled_access(request)
        return self.create_response(request, {'success': objects})


class SalesCycleResource(CRMServiceModelResource):
    '''
    GET Method
    I{URL}:  U{alma.net/api/v1/sales_cycle}

    B{Description}:
    API resource manage Contact's SalesCycles

    @undocumented: prepend_urls, Meta
    '''
    #contact = fields.ToOneField(ContactResource, 'contact')
    contact_id = fields.IntegerField(attribute='contact_id', null=True)
    # activities = fields.ToManyField(
    #     'alm_crm.api.ActivityResource', 'rel_activities',
    #     related_name='sales_cycle', null=True, full=True)
    # products = fields.ToManyField(
    #     'alm_crm.api.ProductResource', 'products',
    #     related_name='sales_cycles', null=True, full=False, readonly=True)
    # product_ids = fields.ToManyField(
    #     'alm_crm.api.ProductResource', 'products',
    #     related_name='sales_cycles', null=True, full=False)
    # owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'owner', null=True, full=True)
    author_id = fields.IntegerField(attribute='owner_id')
    # followers = fields.ToManyField('alm_crm.api.CRMUserResource',
    #                                'followers', null=True, full=True)
    projected_value = fields.ToOneField('alm_crm.api.ValueResource',
                                        'projected_value', null=True,
                                        full=True)
    real_value = fields.ToOneField('alm_crm.api.ValueResource',
                                   'real_value', null=True, full=True)

    stat = fields.ToManyField('alm_crm.api.SalesCycleProductStatResource',
        attribute=lambda bundle: SalesCycleProductStat.objects.filter(sales_cycle=bundle.obj),
        null=True, blank=True, readonly=True, full=True)

    class Meta(CommonMeta):
        queryset = SalesCycle.objects.all().prefetch_related('products')
        resource_name = 'sales_cycle'
        excludes = ['from_date', 'to_date']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        always_return_data = True

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/close%s$" %
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
        ]

    def close(self, request, **kwargs):
        '''
        PUT METHOD
        I{URL}:  U{alma.net/api/v1/sales_cycle/:id/close/}

        B{Description}:
        close SalesCycle, set value of SalesCycleProductStat
        update status to 'C'('Completed')

        @return: updated SalesCycle and close Activity

        '''
        with RequestContext(self, request, allowed_methods=['post', 'get', 'put']):
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
            if obj.is_global:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized(
                                            'Could not close global sales cycle'))
            bundle = self.build_bundle(obj=obj, request=request)

            # get PUT's data from request.body
            deserialized = self.deserialize(
                request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            deserialized = self.alter_deserialized_list_data(request, deserialized)
            sales_cycle, activity = bundle.obj.close(products_with_values=deserialized)

        return self.create_response(
            request, {
                'sales_cycle': SalesCycleResource().get_bundle_detail(sales_cycle, request),
                'activity': ActivityResource().get_bundle_detail(activity, request)
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

            obj.products.clear()
            obj.add_products(deserialized['object_ids'])

            if not self._meta.always_return_data:
                return http.HttpAccepted(location=location)
            else:
                return self.create_response(request, get_product_ids(),
                                            response_class=http.HttpAccepted)


class ActivityResource(CRMServiceModelResource):
    """
    GET Method
    I{URL}:  U{alma.net/api/v1/activity}

    B{Description}:
    API resource to manage SalesCycle's Activities

    @return:  activities
    >>> 'objects': [
    ... {
    ...     'id': 1,
    ...     'resource_uri': '/api/v1/activity/1/',
    ...     'salescycle_id': 1,
    ...     'description': 'd1'
    ...     'feedback': '$',
    ...     'author_id': 2,
    ...     'date_created': '2014-09-11T00:00:00',
    ... }
    ... ]

    @undocumented: Meta
    """

    author_id = fields.IntegerField(attribute='author_id', null=True)
    description = fields.CharField(attribute='description')
    sales_cycle_id = fields.IntegerField(null=True)
    feedback_status = fields.CharField(null=True)

    class Meta(CommonMeta):
        queryset = Activity.objects.all().prefetch_related('recipients')
        resource_name = 'activity'
        excludes = ['date_edited', 'subscription_id', 'title']
        always_return_data = True
        filtering = {
            'author_id': ('exact', ),
            'owner': ALL_WITH_RELATIONS,
            'sales_cycle': ALL_WITH_RELATIONS}

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
                self.wrap_view('get_company_activities'),
                name='api_company_activities'
            ),
            url(
                r"^(?P<resource_name>%s)/contact_activities/(?P<id>\d+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_contact_activities'),
                name='api_contact_activities'
            ),
        ]

    def dehydrate(self, bundle):
        recip = bundle.obj.recipients.filter(
            user__pk=bundle.obj.owner_id).first()
        if not recip or recip.has_read:
            bundle.data['has_read'] = True
        else:
            bundle.data['has_read'] = False

        # send updated contact (status was changed to LEAD)
        if bundle.data.get('obj_created'):
            if len(Contact.get_contact_activities(bundle.obj.contact.id)) == 1:
                bundle.data['contact'] = ContactResource().get_bundle_detail(bundle.obj.contact, bundle.request)
            bundle.data.pop('obj_created')

        return bundle

    def dehydrate_sales_cycle_id(self, bundle):
        return bundle.obj.sales_cycle_id

    def dehydrate_feedback_status(self, bundle):
        if hasattr(bundle.obj, 'feedback'):
            return bundle.obj.feedback.status
        return None

    def build_filters(self, filters=None):
        filters = super(self.__class__, self).build_filters(filters=filters)
        _add_filters, _del_keys = {}, set([])
        for k, v in filters.iteritems():
            if k.startswith('author_id'):
                _add_filters[k.replace('author_id', 'owner__id')] = v
                _del_keys.add(k)

        for k in _del_keys:
            filters.pop(k)
        filters.update(_add_filters)
        return filters

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
        ...         "subscription_id": 1
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
                Activity.mark_as_read(request.user.get_crmuser().id, act_id)
            rv = len(data)
        return self.create_response(
            request, {'success': rv})

    def obj_create(self, bundle, **kwargs):
        act = bundle.obj = self._meta.object_class()
        act.author_id = bundle.data.get('author_id')
        act.description = bundle.data.get('description')
        act.sales_cycle_id = bundle.data.get('sales_cycle_id')
        # if bundle.data.get('sales_cycle_id', None):
        #     act.sales_cycle_id = bundle.data.get('sales_cycle_id')
        # else:
        #     _subscr_id = self.get_crmsubscr_id(bundle.request)
        #     act.sales_cycle_id = SalesCycle.get_global(_subscr_id).pk
        act.save()
        if bundle.data.get('feedback_status'):
            act.feedback = Feedback(
                status=bundle.data.get('feedback_status', None),
                owner_id=act.author_id)
            act.feedback.save()
        act.spray(self.get_crmsubscr_id(bundle.request))
        bundle = self.full_hydrate(bundle)

        bundle.data['obj_created'] = True
        return bundle

    def save(self, bundle, **kwargs):
        bundle = super(ActivityResource, self).save(bundle, **kwargs)
        if bundle.data.get('feedback_status', None):
            if not hasattr(bundle.obj, 'feedback'):
                bundle.obj.feedback = Feedback(
                    status=bundle.data['feedback_status'],
                    owner_id=bundle.obj.author_id)
                bundle.obj.feedback.save()
            if bundle.obj.feedback.status != bundle.data['feedback_status']:
                bundle.obj.feedback.status = bundle.data['feedback_status']
                bundle.obj.feedback.save()
        if bundle.data.get('sales_cycle_id', None):
            new_sc_id = bundle.data.get('sales_cycle_id')
            if bundle.obj.sales_cycle_id != new_sc_id:
                sales_cycle = SalesCycle.objects.get(pk=new_sc_id)
                bundle.obj.sales_cycle = sales_cycle
                bundle.obj.save()
        return bundle


class ProductResource(CRMServiceModelResource):
    '''
    ALL+PATCH Method
    I{URL}:  U{alma.net/api/v1/product/}

    B{Description}:
    API resource to manage SalesCycle's Products


    @undocumented: Meta
    '''
    author_id = fields.IntegerField(attribute='author_id', null=True)
    sales_cycles = fields.ToManyField(SalesCycleResource, 'sales_cycles', readonly=True)

    class Meta(CommonMeta):
        queryset = Product.objects.all()
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
        ]

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
    ... "subscription_id": null,
    ... }

    @undocumented: Meta
    '''
    value = fields.IntegerField(attribute='amount')

    class Meta(CommonMeta):
        queryset = Value.objects.all()
        resource_name = 'sales_cycle/value'
        excludes = ['amount']


class CRMUserResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/crmuser/}

    B{Description}:
    API resource to manage CRMUsers

    @undocumented: Meta
    '''
    user = fields.ToOneField('alm_user.api.UserResource', 'user', null=True, full=True)
    unfollow_list = fields.ToManyField(ContactResource, 'unfollow_list', null=True, full=False)
    vcard = fields.ToOneField('alm_vcard.api.VCardResource', 'vcard', null=True, full=True)

    class Meta(CommonMeta):
        queryset = CRMUser.objects.all()
        resource_name = 'crmuser'

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/follow_unfollow%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('follow_unfollow'),
                name='api_follow_unfollow'
            ),
        ]

    def dehydrate_unfollow_list(self, bundle):
        return [contact.id for contact in bundle.obj.unfollow_list.all()]

    def dehydrate_vcard(self, bundle):
        try:
            user = bundle.obj.get_billing_user()
            return VCardResource().full_dehydrate(
                            VCardResource().build_bundle(
                                obj=VCard.objects.get(id=user.vcard.id))
                            )
        except:
            return None

    def full_dehydrate(self, bundle, for_list=False):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        user = bundle.obj.get_billing_user()
        bundle.data['user'] = user.id
        if user.userpic:
            bundle.data['userpic'] = user.userpic.url
        return bundle

    def follow_unfollow(self, request, **kwargs):
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        contact_ids = data.get('contact_ids', None)
        if contact_ids:
            if type(contact_ids)!=list:
                return self.create_response(
                    request, {'success':False, 'message':'Pass a list as a parameter'}
                    )
        else:
            return self.create_response(
                    request, {'success':False, 'message':'Must pass a contact_ids parameter'}
                    )
        crmuser = request.user.get_crmuser()
        unfollow_list = [contact.id for contact in crmuser.unfollow_list.all()]
        for contact_id in contact_ids:
            if contact_id in unfollow_list:
                crmuser.unfollow_list.remove(contact_id)
            else:
                crmuser.unfollow_list.add(contact_id)
        crmuser.save()
        raise ImmediateHttpResponse(
            HttpResponse(
                content=Serializer().to_json(
                    self.full_dehydrate(
                        self.build_bundle(
                            obj=crmuser)
                        )
                    ),
                content_type='application/json; charset=utf-8', status=200
                )
            )


class ShareResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/share/}

    B{Description}:
    API resource to manage Shares of Contacts

    @undocumented: prepend_urls, Meta
    '''
    contact = fields.ToOneField(ContactResource, 'contact')
    share_to = fields.ToOneField(CRMUserResource, 'share_to',
                                 full=True, null=True)
    share_from = fields.ToOneField(CRMUserResource, 'share_from',
                                   full=True, null=True)

    class Meta(CommonMeta):
        queryset = Share.objects.all()
        resource_name = 'share'
        excludes = ['subscription_id', 'description']

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

        shares = Share.get_shares(self.get_crmsubscr_id(request))
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
                share_from=CRMUser.objects.get(id=int(json_obj.get('share_from'))),
                contact=Contact.objects.get(id=int(json_obj.get('contact'))),
                share_to=CRMUser.objects.get(id=int(json_obj.get('share_to')))
                )
            s.save()
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
        return bundle.obj.contact.id

    def dehydrate_share_from(self, bundle):
        return bundle.obj.share_from.id

    def dehydrate_share_to(self, bundle):
        return bundle.obj.share_to.id

    def hydrate_contact(self, bundle):
        contact = Contact.objects.get(id=bundle.data['contact'])
        bundle.data['contact'] = contact
        return bundle

    def hydrate_share_from(self, bundle):
        share_from = CRMUser.objects.get(id=bundle.data['share_from'])
        bundle.data['share_from'] = share_from
        return bundle

    def hydrate_share_to(self, bundle):
        share_to = CRMUser.objects.get(id=bundle.data['share_to'])
        bundle.data['share_to'] = share_to
        return bundle


class FeedbackResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/feedback/}

    B{Description}:
    API resource to manage Activity's Feedback

    @undocumented: Meta
    '''

    #activity = fields.OneToOneField(ActivityResource, 'activity', related_name='activity_feedback', null=True, full=False)
    # value = fields.ToOneField(ValueResource, 'feedback_value', null=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'owner', null=True, full=True)
    status = fields.CharField(attribute='status')

    class Meta(CommonMeta):
        queryset = Feedback.objects.all()
        resource_name = 'feedback'


class CommentResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/comment/}

    B{Description}:
    API resource to manage Comments
    (GenericRelation with Activity, Contact, Share, Feedback)

    @undocumented: Meta
    '''

    author_id = fields.IntegerField(attribute='owner_id')
    content_object = GenericForeignKeyField({
        Activity: ActivityResource,
        Contact: ContactResource,
        Share: ShareResource,
        Feedback: FeedbackResource
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

        generics = ['activity_id', 'contact_id', 'share_id', 'feedback_id']
        model_name = filter(lambda k: k in generics, bundle.data.keys())[0]
        obj_class = ContentType.objects.get(app_label='alm_crm', model=model_name[:-3]).model_class()
        obj_id = bundle.data[model_name]
        bundle.data['object_id'] = obj_id
        bundle.data['content_object'] = obj_class.objects.get(id=obj_id)
        bundle.data.pop(model_name)
        return bundle


class MentionResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/comment/}

    B{Description}:
    API resource to manage Comments
    (GenericRelation with Contact, SalesCycle, Activity, Feedback, Comment)

    @undocumented: Meta
    '''
    content_object = GenericForeignKeyField({
        Contact: ContactResource,
        SalesCycle: SalesCycleResource,
        Activity: ActivityResource,
        Feedback: FeedbackResource,
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
    users = fields.ToManyField('alm_crm.api.CRMUserResource', 'users',
                               related_name='contact_list', null=True,
                               full=False)

    class Meta(CommonMeta):
        queryset = ContactList.objects.all()
        resource_name = 'contact_list'

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/users%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_users'),
                name='api_get_users'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/check_user%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_user'),
                name='api_check_user'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/add_users%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('add_users'),
                name='api_add_users'
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/delete_user%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('delete_user'),
                name='api_delete_user'
            ),
        ]

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
        ...     users: [
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

    def get_users(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/users}

        Description:
        Api function to return the contact list users

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default
        @return:  contacts

        >>> "objects": [
        ...     {
        ...         "id": 1,
        ...         "resource_uri": "/api/v1/contact_list/1/",
        ...         "subscription_id": null,
        ...         "title": "ALMA Cloud",
        ...         "users": [
        ...         {
        ...             "id": 1,
        ...             "is_supervisor": false,
        ...             "organization_id": 1,
        ...             "resource_uri": "/api/v1/crmuser/1/",
        ...             "subscription_id": 1,
        ...             "user_id": 1
        ...         },
        ...         {
        ...             "id": 2,
        ...             "is_supervisor": false,
        ...             "organization_id": 1,
        ...             "resource_uri": "/api/v1/crmuser/2/",
        ...             "subscription_id": 1,
        ...             "user_id": 2
        ...         }
        ...     ]

        '''
        try:
            contact_list = ContactList.objects.get(id=kwargs.get('id'))
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            users = contact_list.users.all()[offset:offset + limit]
            crm_user_resource = CRMUserResource()
            obj_dict = {}
            obj_dict['objects'] = \
                crm_user_resource.get_bundle_list(users, request)
            return self.create_response(request, obj_dict)
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )

    def check_user(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/check_user}

        Description:
        Api function to return existence user in the contact list

        @type  user_id: number
        @param user_id: User id which you are checking.

        @return:  success and list of boolean fields

        >>> {
        ...    "success": true
        ... }

        '''
        try:
            contact_list = ContactList.objects.get(id=kwargs.get('id'))
            user_id = int(request.GET.get('user_id', 0))
            if not user_id:
                return self.create_response(
                    request,
                    {'success': False, 'error_string': 'User id is not set'}
                    )
            return self.create_response(
                request,
                {'success': ContactList.objects.get(id=kwargs.get('id')).check_user(user_id=user_id)}
                )
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )

    def add_users(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/:id/add_users}

        Description:
        Api function to add users to the contact list

        @type  user_ids: list
        @param user_ids: Adding user ids for adding.

        @return:  success and list of boolean fields

        >>> {
        ...    "success": [True, False, False, True]
        ... }

        '''
        try:
            user_ids = ast.literal_eval(request.GET.get('user_ids'))
            if not user_ids:
                return self.create_response(
                    request,
                    {'success': False, 'error_string': 'User ids is not set'}
                    )
            obj_dict = {}
            obj_dict['success'] = ContactList.objects.get(id=kwargs.get('id')).add_users(user_ids=user_ids)
            return self.create_response(
                request, obj_dict)
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )

    def delete_user(self, request, **kwargs):
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
            user_id = int(request.GET.get('user_id', 0))
            if not user_id:
                return self.create_response(
                    request,
                    {'success': False, 'error_string': 'User id is not set'}
                    )
            return self.create_response(
                request,
                {'success':
                    ContactList.objects.get(id=kwargs.get('id')).delete_user(
                        user_id=user_id)}
                )
        except ContactList.DoesNotExist:
            return self.create_response(
                request,
                {'success': False,
                 'error_string': 'Contact list does not exits'}
                )


class AppStateObject(object):
    '''
    @undocumented: __init__, get_users, get_company, get_contacts,
    get_sales_cycles, get_activities, get_shares, get_constants,
    get_session
    '''

    def __init__(self, service_slug=None, request=None):
        if service_slug is None:
            return
        self.request = request
        self.current_user = request.user
        self.subscription_id = get_subscr_id(request.user_env, service_slug)
        self.company = request.user.get_company()
        self.current_crmuser = \
            request.user.get_subscr_user(self.subscription_id)

        self.objects = {
            'users': self.get_users(),
            'company': self.get_company(),
            'contacts': self.get_contacts(),
            'shares': self.get_shares(),
            'sales_cycles': self.get_sales_cycles(),
            'activities': self.get_activities(),
            'products': self.get_products(),
            'filters': self.get_filters(),
            'sales_cycles_to_products_map': self.get_sales_cycle2products_map()
        }
        self.constants = self.get_constants()
        self.session = self.get_session()

    def get_users(self):
        crmusers, users = CRMUser.get_crmusers(
            self.subscription_id, with_users=True)
        return CRMUserResource().get_bundle_list(crmusers, self.request)

    def get_company(self):
        data = model_to_dict(self.company, fields=['name', 'subdomain', 'id'])
        crmuser = \
            self.company.owner.first().get_subscr_user(self.subscription_id)
        data.update({'owner_id': crmuser.pk})
        return [data]

    def get_contacts(self):
        contacts = Contact.get_contacts_by_last_activity_date(
            self.subscription_id, all=True)

        return ContactResource().get_bundle_list(contacts, self.request)

    def get_sales_cycles(self):
        sales_cycles = SalesCycle.get_salescycles_by_last_activity_date(
            self.subscription_id, all=True, include_activities=False)

        return SalesCycleResource().get_bundle_list(sales_cycles, self.request)

    def get_activities(self):
        activities = Activity.get_activities_by_date_created(
            self.subscription_id, all=True, include_sales_cycles=False)

        return ActivityResource().get_bundle_list(activities, self.request)

    def get_filters(self):
        filters = Filter.get_filters_by_crmuser(self.subscription_id)
        return FilterResource().get_bundle_list(filters, self.request)

    def get_products(self):
        products = Product.get_products(self.subscription_id)
        return ProductResource().get_bundle_list(products, self.request)

    def get_sales_cycle2products_map(self):
        sales_cycles = SalesCycle.get_salescycles_by_last_activity_date(
            self.subscription_id, all=True, include_activities=False)
        data = {}
        for sc in sales_cycles:
            data[sc.id] = list(sc.products.values_list('pk', flat=True))
        return data

    def get_shares(self):
        shares = Share.get_shares_in_for(self.subscription_id)
        return ShareResource().get_bundle_list(shares, self.request)

    def get_constants(self):
        return {
            'sales_cycle': {
                'statuses': SalesCycle.STATUSES_OPTIONS,
                'statuses_hash': SalesCycle.STATUSES_DICT
            },
            'activity': {
                'feedback_options': Feedback.STATUSES_OPTIONS,
                'feedback_hash': Feedback.STATUSES_DICT
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

    def get_session(self):
        return {
            'user_id': self.current_crmuser.pk,
            'session_key': self.request.session.session_key,
            'logged_in': self.current_user.is_authenticated(),
            'language': translation.get_language()
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
    objects = fields.DictField(attribute='objects', readonly=True)
    constants = fields.DictField(attribute='constants', readonly=True)
    session = fields.DictField(attribute='session', readonly=True)

    class Meta:
        resource_name = 'app_state'
        object_class = AppStateObject
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/my_feed%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('my_feed'),
                name='api_my_feed'
            )]

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
        ...         'feedback': 'W'
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
        ...     'feedback': {'statuses': [
        ...             {'W': 'waiting'}, {'$': '1000'}, {'1': 'Client is happy'},
        ...             {'2': 'Client is OK'}, {'3': 'Client is neutral'},
        ...             {'4': 'Client is disappointed'}, {'5': 'Client is angry'}
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
        return AppStateObject(service_slug=kwargs['pk'],
                              request=bundle.request)

    def my_feed(self, request, **kwargs):
        '''
        pass limit and offset with GET request
        '''
        activities, sales_cycles, s2a_map = \
            Activity.get_activities_by_date_created(self.get_crmsubscr_id(request),
                                                    owned=True, mentioned=True,
                                                    include_sales_cycles=True)

        return self.create_response(
            request,
            {
                'sales_cycles': SalesCycleResource().get_bundle_list(sales_cycles, request),
                'activities': ActivityResource().get_bundle_list(activities, request)
            })


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
        return bundle.obj.product.id

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
