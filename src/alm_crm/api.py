from tastypie import fields, http
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.resources import Resource, ModelResource
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper
from django.forms.models import model_to_dict
from django.utils import translation
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
    )
from alm_vcard.models import *
from almanet.models import Subscription, Service
from almanet.settings import DEFAULT_SERVICE
import ast
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper
from tastypie.serializers import Serializer
from django.db import models
# try:
#     from django.views.decorators.csrf import csrf_exempt
# except ImportError:
#     def csrf_exempt(func):
#         return func
# from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse, Unauthorized
from tastypie.exceptions import ImmediateHttpResponse, NotFound
# from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
# from django.utils.cache import patch_cache_control, patch_vary_headers
from tastypie.http import HttpNotFound
from django.http import HttpResponse
import json
import datetime
import time



class CRMServiceModelResource(ModelResource):

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

    @classmethod
    def get_crm_subscription(cls, request):
        user_env = request.user_env
        subscription_pk = None
        if 'subscriptions' in user_env:
            subscription_pk = filter(
                lambda x: user_env['subscription_{}'.format(x)]['slug'] == DEFAULT_SERVICE,
                user_env['subscriptions']
                )[0]
        return subscription_pk

    @classmethod
    def get_crmuser(cls, request):
        subscription_pk = cls.get_crm_subscription(request)
        crmuser = None
        if subscription_pk:
            crmuser = request.user.get_subscr_user(subscription_pk)
        return crmuser

    class Meta:
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication())
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
    followers = fields.ToManyField('alm_crm.api.CRMUserResource', 'followers',
                                   null=True, full=False)
    assignees = fields.ToManyField('alm_crm.api.CRMUserResource', 'assignees',
                                   null=True, full=False)
    sales_cycles = fields.ToManyField(
        'alm_crm.api.SalesCycleResource', 'sales_cycles',
        related_name='contact', null=True, full=False)
    parent = fields.ToOneField(
        'alm_crm.api.ContactResource', 'parent',
        null=True, full=False
        )
    shares = fields.ToManyField(
        'alm_crm.api.ShareResource', 'shares',
        null=True, full=True
        )

    class Meta(CRMServiceModelResource.Meta):
        queryset = Contact.objects.all()
        resource_name = 'contact'

    def post_list(self, request, **kwargs):
        '''
        POST METHOD
        I{URL}:  U{alma.net:8000/api/v1/contact/}

        Description
        Api function for contact creation. It creates contact and vcard objects,
        plust it creates a Share objects, so that the user could see that Contact
        in his feed.

        @type  vcard: dictionary object
        @param vcard: Vcard resource object, look at /api/v1/vcard/ for variable
            names

        @return:  status 201

        >>> example POST payload
        ... {
        ...  "owner": "/api/v1/crmuser/1/",
        ...  "vcard": {
        ...      "given_name":"Barry",
        ...      "family_name":"Allen"
        ...      },
        ...  "comment": "Met this contact on conference"
        ...  }

        '''
        return super(self.__class__, self).post_list(request, **kwargs)

    def obj_create(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)
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

    def obj_delete(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")
        for share in bundle.obj.shares.all():
            share.delete()
        for vcard_rel in bundle.obj.vcard._meta.get_all_related_objects():
            if vcard_rel.model == Contact:
                pass
            else:
                for obj in vcard_rel.model.objects.filter(vcard=bundle.obj.vcard):
                    obj.delete()
        self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
        bundle.obj.delete()

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
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        '''
        Custom representation of followers, assignees etc.
        '''
        bundle.data['assignees'] = []
        for obj in bundle.obj.assignees.all():
            bundle.data['assignees'].append(obj.id)
        bundle.data['followers'] = []
        for obj in bundle.obj.followers.all():
            bundle.data['followers'].append(obj.id)
        bundle.data['sales_cycles'] = []
        for obj in bundle.obj.sales_cycles.all():
            bundle.data['sales_cycles'].append(obj.id)
        del bundle.data['owner']
        del bundle.data['parent']
        del bundle.data['resource_uri']
        try:
            bundle.data['author_id'] = bundle.obj.owner.id
        except:
            bundle.data['author_id'] = None
        try:
            bundle.data['parent_id'] = bundle.obj.parent.id
        except:
            bundle.data['parent_id'] = None
        return bundle


    def full_hydrate(self, bundle, **kwargs):
        t1 = time.time()
        contact_id = kwargs.get('id', None)
        if contact_id:
            bundle.obj = Contact.objects.get(id=int(contact_id))
        else:
            bundle.obj = self._meta.object_class()
            # bundle.obj.owner_id = bundle.request.user.get_crmuser().id
            bundle.obj.save()
        '''
        Go through all field names in the Contact Model and check with
        the json that has been submitted. So if the attribute is there
        then i use bundle.obj and setattr of current field_name to whatever
        i got in a json. If its missing then i just delete it.

        '''
        if bundle.data.get('is_company',""):
            if bundle.data['is_company']==1:
                bundle.obj.tp='co'
            else:
                bundle.obj.tp='user'
        if bundle.data.get('author_id',""):
            bundle.obj.owner_id = int(bundle.data['author_id'])
        if bundle.data.get('parent_id',""):
            bundle.obj.parent_id = int(bundle.data['parent_id'])
        for field_name in bundle.obj._meta.get_all_field_names():
            if bundle.data.get(field_name, None):
                field_object = ast.literal_eval(str(bundle.data.get(field_name, None)))
                if isinstance(field_object, str):
                    bundle.obj.__setattr__(field_name, field_object)
                elif isinstance(field_object, list):
                    for obj in field_object:
                        bundle.obj.__getattribute__(field_name).add(int(obj))
                elif isinstance(field_object, dict):
                    t2 = time.time() - t1
                    print "Time to finish contact hydration = %s seconds" % t2
                    self.vcard_full_hydrate(bundle)
                    t3 = time.time() - t2
                    print "Time to finish vcard hydration = %s seconds" % t2
        bundle.obj.save()
        if bundle.data.get('note') and not kwargs.get('id'):
            share = Share(
                    description=bundle.data.get('note'),
                    share_to_id=int(bundle.data['author_id']),
                    share_from_id=int(bundle.data['author_id']),
                    contact_id=bundle.obj.id
                    )
            share.save()
        return bundle

    def vcard_full_hydrate(self, bundle):
        field_object = bundle.data.get('vcard',{})
        if bundle.obj.vcard:
            vcard = bundle.obj.vcard
        else:
            vcard = VCard()
            vcard.save()
            vcard.contact = bundle.obj
        vcard_fields = list(VCard._meta.get_fields_with_model())
        for vcard_field in vcard_fields:
            if vcard_field[0].__class__==models.fields.AutoField:
                pass
            elif vcard_field[0].__class__==models.fields.IntegerField:
                pass
            elif vcard_field[0].__class__==models.fields.DateField:
                attname = vcard_field[0].attname
                bday = field_object.get(attname, "")
                '''
                format = yyyy-mm-dd
                '''
                if bday:
                    bday = datetime.datetime.strptime(bday, '%Y-%m-%d').date()
                    vcard.__setattr__(attname, bday)
            elif vcard_field[0].__class__==models.fields.DateTimeField:
                attname = vcard_field[0].attname
                rev = field_object.get(attname, "")
                if rev:
                    rev = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
                    vcard.__setattr__(attname, bday)
            elif vcard_field[0].__class__==models.fields.CharField:
                attname = vcard_field[0].attname
                vcard.__setattr__(attname,
                    field_object.get(attname, ""))
        '''
        Now i need to go over the list of vcard keys
        check their model names, go through each and every
        model and check for three things
        1) if id is set, then change the values in json
        2) if id is not set, then create
        3) if models are missing then delete the missing values
        '''
        vcard_rel_fields = vcard._meta.get_all_related_objects()

        for vcard_field in vcard_rel_fields:
            if vcard_field.model == Contact:
                pass
            else:
                field_value = vcard_field.var_name+'s'
                obj_list = ast.literal_eval(str(field_object.get(vcard_field.var_name+'s','None')))
                vcard_field_name = vcard_field.var_name+'_set'
                model = vcard.__getattribute__(vcard_field_name).model
                if obj_list:
                    queryset = vcard.__getattribute__(vcard_field_name).all()
                    json_objects = obj_list
                    id_list = []
                    for obj in json_objects:
                        if obj.get('id',None):
                            vcard_obj = model.objects.get(id=int(obj.get('id',None)))
                            del obj['id']
                        else:
                            vcard_obj = model()
                        for key, value in obj.viewitems():
                            vcard_obj.__setattr__(key, value)
                        vcard_obj.vcard = vcard
                        vcard_obj.save()
                        id_list.append(vcard_obj.id)
                    for obj in queryset:
                        if not obj.id in id_list:
                            obj.delete()
                else:
                    for obj in model.objects.filter(vcard=vcard):
                        obj.delete()
        vcard.save()

    def save(self, bundle, skip_errors=False):
        self.is_valid(bundle)

        if bundle.errors and not skip_errors:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

        # Check if they're authorized.
        if bundle.obj.pk:
            self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        else:
            self.authorized_create_detail(self.get_object_list(bundle.request), bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        #If Contact is saved with a small note/comment
        # Save the main object.
        
        if bundle.data['owner_id']:
            bundle.obj.owner_id=int(bundle.data['owner_id'])
        bundle.obj.save()
        try:
            if bundle.data['note']:
                note = bundle.data['note']
                share = Share(
                    note=note,
                    share_to_id=bundle.obj.owner.id,
                    share_from_id=bundle.obj.owner.id,
                    contact_id=bundle.obj.id
                    )
                share.save()
        except KeyError:
            bundle.obj.save()
        bundle.objects_saved.add(self.create_identifier(bundle.obj))
        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

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
                r"^(?P<resource_name>%s)/import_contacts_from_vcard%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('import_contacts_from_vcard'),
                name='api_import_contacts_from_vcard'
            ),
            url(
                r"^(?P<resource_name>%s)/export_contacts_to_vcard%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('export_contacts_to_vcard'),
                name='api_export_contacts_to_vcard'
            ),
        ]

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
            user_id=request.user.id,
            include_activities=include_activities,
            owned=owned,
            assigned=assigned,
            followed=followed,
            limit=limit,
            offset=offset)
        if not include_activities:
            return self.create_response(
                request,
                {'objects': self.get_bundle_list(contacts, request)}
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
        contacts = Contact.get_cold_base(limit, offset)
        return self.create_response(
            request,
            {'objects': self.get_bundle_list(contacts, request)}
            )

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
        STATUS_LEAD = 1
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        contacts = Contact.get_contacts_by_status(STATUS_LEAD, limit, offset)
        return self.create_response(
            request,
            {'objects': self.get_bundle_list(contacts, request)}
            )

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
        products = Contact.get_contact_products(contact_id, limit=limit,
                                                offset=offset)

        product_resource = ProductResource()
        obj_dict = {}
        obj_dict['objects'] = product_resource.get_bundle_list(products,
                                                               request)
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
        activities = Contact.get_contact_activities(contact_id, limit=limit,
                                                    offset=offset)

        activity_resource = ActivityResource()
        obj_dict = {}
        obj_dict['objects'] = activity_resource.get_bundle_list(activities,
                                                                request)
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
            search_text=search_text,
            search_params=search_params,
            order_by=order_by,
            limit=limit,
            offset=offset)
        return self.create_response(
            request,
            {'objects': self.get_bundle_list(contacts, request)}
            )

    def assign_contact(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/assign_contact/}

        Description
        Assign a signle user to a signle contact

        @type  user_id: number
        @param user_id: user id
        @type  contact_id: number
        @param contact_id: contact id


        @return: json.

        >>>
        ... {
        ...     'success':True
        ... },
        '''
        user_id = int(request.GET.get('user_id', 0))
        if not user_id:
            return self.create_response(
                request,
                {'success': False, 'error_string': 'User id is not set'}
                )
        contact_id = int(request.GET.get('contact_id', 0))
        if not contact_id:
            return self.create_response(
                request,
                {'success': False, 'error_string': 'Contact id is not set'}
                )
        return self.create_response(
            request,
            {'success': Contact.assign_user_to_contact(user_id, contact_id)}
            )

    def assign_contacts(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/contact/assign_contacts/}

        Description
        Assign a single user to multiple contacts

        @type  user_id: number
        @param user_id: user id
        @type  contact_ids: list
        @param contact_ids: List of contact ids, [1,2,3]


        @return: json.

        >>>
        ... {
        ...     'success':True
        ... },
        '''
        user_id = int(request.GET.get('user_id', 0))
        if not user_id:
            return self.create_response(
                request,
                {'success': False, 'error_string': 'User id is not set'}
                )
        contact_ids = ast.literal_eval(request.GET.get('contact_ids', []))
        if not contact_ids:
            return self.create_response(
                request,
                {'success': False, 'error_string': 'Contact ids are not set'}
                )
        return self.create_response(
            request,
            {'success': Contact.assign_user_to_contacts(user_id, contact_ids)}
            )

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

    def import_contacts_from_vcard(self, request, **kwargs):
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
        if request.method == 'POST':
            return self.create_response(
                request,
                Contact.import_contacts_from_vcard(request.FILES['myfile'])
                )

    def export_contacts_to_vcard(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net:8000/api/v1/contact/export_contacts_to_vcard/}

        Description
        Export selected contacts to vcard.txt file

        @type  contact_ids: list
        @param contact_ids: A list of contact ids like so [1,2,3]

        @return: file disposition.

        >>> if list is empty returns
        ... No contacts have been selected
        ...
        >>> if contact id doesn't exist returns:
        ... Contact with id=contact_id does not exist

        '''
        contact_ids = ast.literal_eval(request.GET.get('contact_ids', []))
        if contact_ids:
            temp = NamedTemporaryFile()
            response = HttpResponse(FileWrapper(temp), mimetype='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="%s.txt"' % 'vcard'
            for contact_id in contact_ids:
                try:
                    vcard = Contact.objects.get(id=contact_id).vcard
                    response.write(vcard.exportTo('vCard'))
                except:
                    return HttpResponse('Contact with id=%s does not exist' % contact_id)
            return response
        else:
            return HttpResponse('No contacts have been selected')


class SalesCycleResource(CRMServiceModelResource):
    '''
    GET Method
    I{URL}:  U{alma.net/api/v1/sales_cycle}

    B{Description}:
    API resource manage Contact's SalesCycles

    @undocumented: prepend_urls, Meta
    '''
    #contact = fields.ForeignKey(ContactResource, 'contact')
    contact_id = fields.IntegerField(attribute='contact_id')
    # activities = fields.ToManyField(
    #     'alm_crm.api.ActivityResource', 'rel_activities',
    #     related_name='sales_cycle', null=True, full=True)
    product_ids = fields.ToManyField(
        'alm_crm.api.ProductResource', 'products',
        related_name='sales_cycles', null=True, full=False)
    # owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'owner', null=True, full=True)
    owner_id = fields.IntegerField(attribute='owner_id')
    # followers = fields.ToManyField('alm_crm.api.CRMUserResource',
    #                                'followers', null=True, full=True)
    projected_value = fields.ToOneField('alm_crm.api.ValueResource',
                                        'projected_value', null=True,
                                        full=True)
    real_value = fields.ToOneField('alm_crm.api.ValueResource',
                                   'real_value', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = SalesCycle.objects.all()
        resource_name = 'sales_cycle'
        excludes = ['from_date', 'to_date']

    def dehydrate_date_created(self, bundle):
        return bundle.obj.date_created.strftime('%Y-%m-%d %H:%M')

    def dehydrate_product_ids(self, bundle):
        return list(bundle.obj.products.values_list('pk', flat=True))

    def hydrate_product_ids(self, bundle):
        ids = bundle.data.get('product_ids', [])
        # check to prevent second run, because hydrate runs twice
        if len(ids) > 0 and type(ids[0]) == int:
            ids = map(int, ids)
            bundle.data['product_ids'] = Product.objects.filter(id__in=ids)
        return bundle

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/finish%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('finish'),
                name='api_finish'
            ),
        ]

    def finish(self, request, **kwargs):
        '''
        PUT METHOD
        I{URL}:  U{alma.net/api/v1/sales_cycle/finish/}

        B{Description}:
        finish SalesCycle by
        setting real_value and update status to 'C' ('Completed')

        @type  amount: number
        @param amount: Amount of real_value
        @type  salary: string (optional)
        @param salary: Salary type of real_value: [monthly|annualy|instant]
        @type  currency: string (optional)
        @param currency: Currency type of real_value: [KZT|USD|RUB]


        @return: updated SalesCycle

        >>> {
        ...     'id': 1,
        ...     'resource_uri': '/api/v1/sales_cycle/1/'
        ...     'status': 'C',
        ...     'real_value': {
        ...         'salary': 'monthly',
        ...         'currency': 'KZT',
        ...         'amount': 1000,
        ...         'subscription_id': 1,
        ...         'id': 8,
        ...         'resource_uri': '/api/v1/sales_cycle/value/8/'
        ...     },
        ...     'projected_value': {
        ...         'salary': 'monthly',
        ...         'currency': 'KZT',
        ...         'amount': 100000,
        ...         'subscription_id': 1,
        ...         'id': 1,
        ...         'resource_uri': '/api/v1/sales_cycle/value/1/'
        ...     },
        ...     'activities': [],
        ...     'contact': '/api/v1/contact/1/',
        ...     'from_date': '2014-09-10T00:00:00',
        ...     'to_date': '2014-09-10T00:00:00',
        ...     'owner': {...}
        ...     'date_created': u'2014-09-10T00:00:00',
        ...     'subscription_id': 1,
        ...     'followers': []
        ... }
        '''
        self.method_check(request, allowed=['put'])

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

        if deserialized.get('value', False):
            real_value = {
                'amount': deserialized.get('value'),
                'salary': deserialized.get('salary'),
                'currency': deserialized.get('currency')
                }

            # backend function to set real_value and update status
            bundle.obj.finish(**real_value)
        else:
            return http.HttpBadRequest(
                content="must be provided 'value' value of 'real_value'",
                content_type='text/plain')

        if not hasattr(self.Meta, 'always_return_data') or \
                not self.Meta.always_return_data:
            return http.HttpNoContent()
        else:
            bundle = self.full_dehydrate(bundle)
            bundle = self.alter_detail_data_to_serialize(request, bundle)
            return self.create_response(request, bundle)


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
    ...     'sales_cycle_id': 1,
    ...     'description': 'd1'
    ...     'author_id': 2,
    ...     'date_created': '2014-09-11T00:00:00',
    ... }
    ... ]


    @undocumented: Meta
    """
    author_id = fields.IntegerField(attribute='author_id', null=True)
    description = fields.CharField(attribute='description')
    sales_cycle = fields.ForeignKey(SalesCycleResource, 'sales_cycle')
    feedback = fields.ToOneField('alm_crm.api.FeedbackResource', 'feedback', null=True, blank=True)


    # comments = fields.ToManyField(
    #     'alm_crm.api.CommentResource',
    #     attribute=lambda bundle: Comment.objects.filter(
    #         content_type=ContentType.objects.get_for_model(bundle.obj),
    #         object_id=bundle.obj.id
    #         ),
    #     null=True, full=True
    #     )
    # mention_users = fields.ToManyField(
    #     'alm_crm.api.CRMUserResource',
    #     attribute=lambda bundle: CRMUser.objects.filter(
    #         pk__in=Mention.objects.filter(
    #             content_type=ContentType.objects.get_for_model(bundle.obj),
    #             object_id=bundle.obj.id
    #         ).values_list('user_id', flat=True).distinct()
    #         ),
    #     null=True, full=False
    #     )

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/comments%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_comments'),
                name='api_get_comments'
            )
        ]


    def dehydrate_sales_cycle(self, bundle):
        return bundle.obj.sales_cycle.id

    def dehydrate_feedback(self, bundle):
        return hasattr(bundle.obj, 'feedback') and bundle.obj.feedback.status or None

    def hydrate_sales_cycle(self, bundle):
        sales_cycle = SalesCycle.objects.get(id = bundle.data['sales_cycle'])
        bundle.data['sales_cycle'] = sales_cycle
        return bundle

    def hydrate_feedback(self, bundle):
        # feedback = Feedback()
        # if bundle.request.method == "PUT":
        #     feedback = Activity.objects.get(id=bundle.data['id']).feedback
        #     feedback.status = bundle.data['feedback']
        # elif bundle.request.method == "POST" and bundle.data.get('feedback', None):
        #     feedback.status = bundle.data['feedback']
        #     feedback.owner = CRMUser.objects.get(id=bundle.data['author_id'])
        # else:
        #      feedback.owner = CRMUser.objects.get(id=bundle.data['author_id'])
        #      feedback.status = 'W'

        # bundle.data['feedback'] = feedback
        # feedback.save()

        if bundle.data.get('feedback'):
            bundle.data['feedback_status'] = bundle.data['feedback']
            bundle.data['feedback'] = None

        return bundle
    
    def get_comments(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/activity/:id/comments}

        Description:
        Api function to return comments of the activity
        @return:  comments

        >>> "objects": [
        ...     {
        ...         "comment": "Test comment 1",
        ...         "content_object": "/api/v1/activity/1/",
        ...         "date_created": "2014-09-10T00:00:00",
        ...         "date_edited": "2014-12-29T09:45:24.166720",
        ...         "id": 1,
        ...         "object_id": 1,
        ...         "resource_uri": "",
        ...         "subscription_id": 1
        ...         }
        ...     ]

        '''

        try:
            activity = Activity.objects.get(id=kwargs.get('id'))
            comments = activity.comments.all()
            comment_resource = CommentResource()
            obj_dict = {}
            obj_dict['objects'] = comment_resource.get_bundle_list(comments,
                                                                   request)
            return self.create_response(request, obj_dict)
        except ContactList.DoesNotExist:
            return self.create_response(
                    request, {'success':False, 'error_string':'Has no any comments'}
                )


    def save(self, bundle, skip_errors=False):
        bundle = super(self.__class__, self).save(bundle, skip_errors)
        status = 'W'
        feedback = None
        if bundle.data.get('feedback_status', None):
            status = bundle.data['feedback_status']
        if bundle.request.method == 'PUT':
            feedback = Feedback.objects.get(activity = bundle.obj)
            feedback.status = status
        else:        
            feedback = Feedback(owner = bundle.obj.owner,
                                activity = bundle.obj,
                                 status = status)
        feedback.save()
        bundle.data['feedback'] = feedback
        return bundle

    class Meta(CRMServiceModelResource.Meta):
        queryset = Activity.objects.all()
        resource_name = 'activity'
        excludes = ['date_edited', 'subscription_id', 'title']
        always_return_data = True

    def post_list(self, request, **kwargs):
        '''
        POST METHOD
        I{URL}:  U{alma.net/api/v1/activity/}

        Description
        API standart function to Create new Activity

        @type  mention_user_ids: list[id]
        @param mention_user_ids: The list of crmuser ids,
        to add them as mentioned users of new activity

        @return: HTTP status code back (201) and a Location header,
        which gives us the URI to our newly created resource.

        >>> HTTP/1.0 201 CREATED
        ... Date: Fri, 11 Nov 2014 06:48:36 GMT
        ... Server: WSGIServer/0.1 Python/2.7
        ... Content-Type: text/html; charset=utf-8
        ... Location: http://alma.net/api/v1/activity/1/
        '''
        return super(self.__class__, self).post_list(request, **kwargs)


class ProductResource(CRMServiceModelResource):
    '''
    ALL+PATCH Method
    I{URL}:  U{alma.net/api/v1/product/}

    B{Description}:
    API resource to manage SalesCycle's Products


    @undocumented: Meta
    '''
    sales_cycles = fields.ToManyField(SalesCycleResource, 'sales_cycles')

    class Meta(CRMServiceModelResource.Meta):
        queryset = Product.objects.all()
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        resource_name = 'product'


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

    class Meta(CRMServiceModelResource.Meta):
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

    class Meta(CRMServiceModelResource.Meta):
        queryset = CRMUser.objects.all()
        resource_name = 'crmuser'


class ShareResource(CRMServiceModelResource):
    '''
    ALL Method
    I{URL}:  U{alma.net/api/v1/share/}

    B{Description}:
    API resource to manage Shares of Contacts

    @undocumented: prepend_urls, Meta
    '''
    contact = fields.ForeignKey(ContactResource, 'contact')
    share_to = fields.ForeignKey(CRMUserResource, 'share_to',
                                 full=True, null=True)
    share_from = fields.ForeignKey(CRMUserResource, 'share_from',
                                   full=True, null=True)
    note = fields.CharField(attribute='description', null = True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Share.objects.all()
        resource_name = 'share'
        excludes = ['is_read', 'subscription_id', 'description']

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/recent%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_shares'),
                name='api_last_shares'
            ),
        ]

    def get_last_shares(self, request, **kwargs):
        '''
        pass limit and offset  with GET request
        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        shares = Share().get_shares(limit=limit, offset=offset)
        return self.create_response(
            request,
            {'objects': self.get_bundle_list(shares, request)}
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

    class Meta(CRMServiceModelResource.Meta):
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
    content_object = GenericForeignKeyField({
        Activity: ActivityResource,
        Contact: ContactResource,
        Share: ShareResource,
        Feedback: FeedbackResource
    }, 'content_object')

    def dehydrate_date_created(self, bundle):
        return bundle.obj.date_created.strftime('%Y-%m-%d %H:%M')

    def dehydrate_date_edited(self, bundle):
        return bundle.obj.date_edited.strftime('%Y-%m-%d %H:%M')

    class Meta(CRMServiceModelResource.Meta):
        queryset = Comment.objects.all()
        resource_name = 'comment'


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

    class Meta(CRMServiceModelResource.Meta):
        queryset = Mention.objects.all()
        resource_name = 'mention'


class ContactListResource(CRMServiceModelResource):
    users = fields.ToManyField('alm_crm.api.CRMUserResource', 'users',
                               related_name='contact_list', null=True,
                               full=False)

    class Meta(CRMServiceModelResource.Meta):
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
        service = Service.objects.get(slug=service_slug)

        self.request = request
        self.current_user = request.user
        self.subscription = self.current_user.get_subscr_by_service(service)
        self.company = self.subscription.organization
        self.current_crmuser = \
            request.user.get_subscr_user(self.subscription.pk)

        self.objects = {
            'users': self.get_users(),
            'company': self.get_company(),
            'contacts': self.get_contacts(),
            'shares': self.get_shares(),
            'sales_cycles': self.get_sales_cycles(),
            'activities': self.get_activities(),
            'products': self.get_products(),
        }
        self.constants = self.get_constants()
        self.session = self.get_session()

    def get_users(self):
        crmusers, users = CRMUser.get_crmusers(with_users=True)

        def _map(crmuser):
            data = model_to_dict(users.get(pk=crmuser.user_id), fields=[
                'email', 'first_name', 'last_name', 'is_admin'])
            data.update({'id': crmuser.pk, 'company_id': self.company.pk})
            return data

        return map(_map, crmusers)

    def get_company(self):
        data = model_to_dict(self.company, fields=['name', 'subdomain', 'id'])
        crmuser = \
            self.company.owner.first().get_subscr_user(self.subscription.pk)
        data.update({'owner_id': crmuser.pk})
        return [data]

    def get_contacts(self):
        contacts = Contact.get_contacts_by_last_activity_date(
            self.current_crmuser.pk, owned=True, assigned=True, followed=True,
            in_shares=True)

        def _get_vcard(vcard):
            data = {}
            data.update({
                'fn': vcard.fn,
                'org': {
                    'id': None,  # TODO
                    'value': vcard.org_set.first() and
                        vcard.org_set.first().organization_name},
                'emails': map(lambda e: model_to_dict(
                    e, fields=['id', 'type', 'value']), vcard.email_set.all()),
                'phones': map(lambda p: model_to_dict(
                    p, fields=['id', 'type', 'value']), vcard.tel_set.all()),
                'urls': map(lambda u: model_to_dict(
                    u, fields=['id', 'type', 'value']), vcard.url_set.all()),
                'adrs': map(lambda a: model_to_dict(
                    a, fields=['id', 'type', 'street_address', 'region',
                               'locality', 'country_name', 'postal_code']
                    ), vcard.adr_set.all()),
                })
            return data

        def _map(contact):
            data = model_to_dict(contact, fields=['id', 'status', 'tp'])
            parent_id = contact.parent and contact.parent.pk
            data.update({
                'parent_id': parent_id,
                'vcard': _get_vcard(contact.vcard),
                'owner_id': contact.owner.pk,
                'date_created': contact.date_created.strftime('%Y-%m-%d %H:%M')
                })
            return data

        return map(_map, contacts)

    def get_sales_cycles(self):
        sales_cycles = SalesCycle.get_salescycles_by_last_activity_date(
            self.current_crmuser.pk, all=True, include_activities=False)

        return SalesCycleResource().get_bundle_list(sales_cycles, self.request)

    def get_activities(self):
        activities = Activity.get_activities_by_date_created(
            self.current_crmuser.pk, all=True, include_sales_cycles=False)

        return ActivityResource().get_bundle_list(activities, self.request)

    def get_products(self):
        products = Product.get_products()

        def _map(p):
            data = model_to_dict(p,
                fields=['id', 'name', 'description', 'price', 'currency'])
            data.update({'owner_id': p.owner.pk})
            return data

        return map(_map, products)

    def get_shares(self):
        shares = Share.get_shares_owned_for(self.current_crmuser.pk)

        def _map(share):
            data = model_to_dict(share,
                                 fields=['id', 'share_to', 'share_from'])
            data.update({
                'note': None,  # TODO
                'contact_id': share.contact.pk,
                'date_created': share.date_created.strftime('%Y-%m-%d %H:%M'),
                })
            return data

        return map(_map, shares)

    def get_constants(self):
        return {
            'salescycle': {'statuses': map(lambda s: {s[0]: s[1]},
                                           SalesCycle.STATUS_OPTIONS)},
            'feedback': {'statuses': map(lambda s: {s[0]: s[1]},
                                         Feedback.STATUS_OPTIONS)},
            'contacts': {
                'statuses': map(lambda s: {s[0]: s[1]}, Contact.STATUS_CODES),
                'tp': map(lambda t: {t[0]: t[1]}, Contact.TYPES_WITH_CAPS)
            },
            'vcard__email': {'types': map(lambda s: {s[0]: s[1]},
                                          Email.TYPE_CHOICES)},
            'vcard__adr': {'types': map(lambda s: {s[0]: s[1]},
                                        Adr.TYPE_CHOICES)},
            'vcard__phone': {'types': map(lambda s: {s[0]: s[1]},
                                          Tel.TYPE_CHOICES)},
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
        current_crmuser = CRMServiceModelResource.get_crmuser(request)

        activities, sales_cycles, s2a_map = Activity.get_activities_by_date_created(
            current_crmuser.pk, owned=True, mentioned=True,
            include_sales_cycles=True, limit=100000)

        def _map_activity(a):
            data = model_to_dict(a, fields=['id', 'description'])
            try:
                feedback_status = a.feedback.status
            except Feedback.DoesNotExist:
                feedback_status = None
            data.update({
                'salescycle_id': a.sales_cycle.pk,
                'author_id': a.owner.pk,
                'feedback': feedback_status,
                'date_created': a.date_created.strftime('%Y-%m-%d %H:%M')
                })
            return data

        def _map_sales_cycle(sc):
            data = model_to_dict(sc, fields=['id', 'title', 'status'])
            data.update({
                'owner_id': sc.owner.pk,
                'contact_id': sc.contact.pk,
                'description': None,  # TODO
                'date_created': sc.date_created.strftime('%Y-%m-%d %H:%M'),
                'product_ids': sc.products.values_list('pk', flat=True),
                'projected_value': {
                    'id': sc.projected_value and sc.projected_value.pk,
                    'value': sc.projected_value and sc.projected_value.amount},
                'real_value': {
                    'id': sc.real_value and sc.real_value.pk,
                    'value': sc.real_value and sc.real_value.amount}
                })
            return data

        activities = map(_map_activity, activities)
        sales_cycles = map(_map_sales_cycle, sales_cycles)

        return self.create_response(
            request,
            {'sales_cycles': sales_cycles, 'activities': activities}
            # {'objects': self.get_bundle_list(shares, request)}
            )
