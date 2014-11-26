from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from django.http import HttpResponse
from tastypie.utils import trailing_slash
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from django.conf.urls import url
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
    )
from almanet.settings import DEFAULT_SERVICE
import ast


class CRMServiceModelResource(ModelResource):

    def hydrate(self, bundle):
        """
        bundle.request.user_env is empty dict{}
        because bundle.request.user is AnonymousUser
        it happen when tastypie uses BasicAuthentication or another
        which doesn't have session
        """
        user_env = bundle.request.user_env

        if 'subscriptions' in user_env:
            bundle.obj.subscription_pk = filter(
                lambda x: user_env['subscription_{}'.format(x)]['slug'] == DEFAULT_SERVICE,
                user_env['subscriptions'])[0]
            bundle.obj.owner = bundle.request.user.get_subscr_user(
                bundle.obj.subscription_pk)

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

    class Meta:
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication())
        authorization = Authorization()


class ContactResource(CRMServiceModelResource):
    vcard = fields.ToOneField('alm_vcard.api.VCardResource', 'vcard',
                              null=True, full=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'owner',
                              null=True, full=True)
    followers = fields.ToManyField('alm_crm.api.CRMUserResource', 'followers',
                                   null=True, full=True)
    assignees = fields.ToManyField('alm_crm.api.CRMUserResource', 'assignees',
                                   null=True, full=True)
    sales_cycles = fields.ToManyField(
        'alm_crm.api.SalesCycleResource', 'sales_cycles',
        related_name='contact', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Contact.objects.all()
        resource_name = 'contact'
        extra_actions = [
        {
            "name": "recent",
            "http_method": "GET",
            "resource_type": "list",
            "summary": "Get contacts ordered by their last activity date",
            "fields": {
                "limit": {
                    "type": "int",
                    "required": False,
                    "description": "Limit queryset, if not provided gives 20\
                     results by default"
                },
                "offset": {
                    "type": "int",
                    "required": False,
                    "description": "offset queryset, if not provided gives 0\
                     by default"
                },
                "owned": {
                    "type": "boolean True or False",
                    "required": False,
                    "description": "if True then includes contacts owned by user,\
                     if False then doesn't include, True by default"
                },
                "assigned": {
                    "type": "boolean True or False",
                    "required": False,
                    "description": "if True then includes contacts assigned to user,\
                     if False then doesn't include, True by default"
                },
                "followed": {
                    "type": "boolean True or False",
                    "required": False,
                    "description": "if True then includes contacts followed by user,\
                     if False then doesn't include, True by default"
                },

            }
        },
        {
            "name": "cold_base",
            "http_method": "GET",
            "resource_type": "list",
            "summary": "Get cold base of contacts, which are contacts \
            which do not have any activities yet",
            "fields": {
                "limit": {
                    "type": "int",
                    "required": False,
                    "description": "Limit queryset, if not provided gives 20 \
                    results by default"
                },
                "offset": {
                    "type": "int",
                    "required": False,
                    "description": "offset queryset, if not provided gives 0 \
                    by default"
                },
            }
        },
        {
            "name": "assign_contact",
            "http_method": "GET",
            "resource_type": "view",
            "summary": "Assign a single contact to a user, return True in\
            case of success, anf False if not",
            "fields": {
                "user_id": {
                    "type": "int",
                    "required": True,
                    "description": "User id to which you want to assign the contact"
                },
                "contact_id": {
                    "type": "int",
                    "required": True,
                    "description": "Id of contact you want to assign to a user"
                },
            }
        },
        {
            "name": "assign_contacts",
            "http_method": "GET",
            "resource_type": "view",
            "summary": "Assign multiple contacts to a user, return True in\
            case of success, anf False if not",
            "fields": {
                "user_id": {
                    "type": "int",
                    "required": True,
                    "description": "User id to which you want to assign the contact"
                },
                "contact_ids": {
                    "type": "list",
                    "required": True,
                    "description": "Ids of contacts you want to assign to a user\
                    in structure of a list like so: [1,2,3...n]"
                },
            }
        },
        {
            "name": "share_contact",
            "http_method": "GET",
            "resource_type": "list",
            "description": "Share a single contact to a user, return True in\
            case of success, anf False if not",
            "fields": {
                "share_from": {
                    "type": "int",
                    "required": True,
                    "description": "User id from which you want to share the contact"
                },
                "share_to": {
                    "type": "int",
                    "required": True,
                    "description": "User id to which you want to share the contact"
                },
                "contact_id": {
                    "type": "int",
                    "required": True,
                    "description": "Id of contact you want to share to a user"
                },
            }
        },
        {
            "name": "share_contacts",
            "http_method": "GET",
            "resource_type": "list",
            "description": "Share multiple contacts with a user, return True in\
            case of success, anf False if not",
            "fields": {
                "share_from": {
                    "type": "int",
                    "required": True,
                    "description": "User id from which you want to share the contact"
                },
                "share_to": {
                    "type": "int",
                    "required": True,
                    "description": "User id to which you want to share the contact"
                },
                "contact_ids": {
                    "type": "list",
                    "required": True,
                    "description": "Ids of contacts you want to assign to a user\
                    in structure of a list like so: [1,2,3...n]"
                },
            }
        },
        {
            "name": "leads",
            "http_method": "GET",
            "resource_type": "list",
            "summary": "Returns all contacts with status 'LEAD'",
            "fields": {
                "limit": {
                    "type": "int",
                    "required": False,
                    "description": "Limit queryset, if not provided gives \
                    20 results by default"
                },
                "offset": {
                    "type": "int",
                    "required": False,
                    "description": "offset queryset, if not provided gives \
                    0 by default"
                }
            }
        },
        {
            "name": "get_products",
            "http_method": "GET",
            "resource_type": "list",
            "summary": "get products by contact \
                (you can get it from salescycle by contact)",
            "fields": {
                "limit": {
                    "type": "int",
                    "required": False,
                    "description": "Limit queryset, if not provided gives \
                    20 results by default"
                },
                "offset": {
                    "type": "int",
                    "required": False,
                    "description": "offset queryset, if not provided gives \
                    0 by default"
                }
            }
        },
        {
            "name": "get_activities",
            "http_method": "GET",
            "resource_type": "list",
            "summary": "get latest activities with embeded comments by contact",
            "fields": {
                "limit": {
                    "type": "int",
                    "required": False,
                    "description": "Limit queryset, if not provided gives \
                    20 results by default"
                },
                "offset": {
                    "type": "int",
                    "required": False,
                    "description": "offset queryset, if not provided gives \
                    0 by default"
                },
            }
        },
        {
            "name": "search",
            "http_method": "GET",
            "resource_type": "list",
            "summary": "Performs a recursive contat search by query and \
            search_params",
            "fields": {
                "limit": {
                    "type": "int",
                    "required": False,
                    "description": "Limit queryset, if not provided gives \
                     20 results by default"
                },
                "offset": {
                    "type": "int",
                    "required": False,
                    "description": "offset queryset, if not provided gives \
                    0 by default"
                },
                "search_text": {
                    "type": "string",
                    "required": False,
                    "description": "It is what it is, a text by which the  \
                    search is performed"
                },
                "order_by": {
                    "type": "string",
                    "required": False,
                    "description": "pass a parameter by which the queryset's \
                    going to be ordered, look at vcard values for reference. If the value is not in \
                    vcard itself but in additional vcard object prepend 'objname__' to it.\
                    Eg. 'vcard__email__value', 'vcard__tel__type. Add 'asc' or 'desc' \
                    for sort order list to be in ascending or descending order. \
                    put both parameters in format of a list Eg. ['fn','asc']."
                },
                "search_params": {
                    "type": "list of tupples example [('fn', 'startswith')]",
                    "required": False,
                    "description": "List of tupples of vcard field value and filter parameter\
                    .Reference this api doc and find vcard values in order to know which search \
                    params do you actually want to use for your request. If the value is not in \
                    vcard itself but in additional vcard object prepend 'objname__' to it.\
                    Eg. 'email__value', 'tel__type"
                }
            }
        }
    ]

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
                name = 'api_share_contact'
            ),
            url(
                r"^(?P<resource_name>%s)/share_contacts%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('share_contacts'),
                name = 'api_share_contacts'
            ),
            url(
                r"^(?P<resource_name>%s)/import_contacts_from_vcard%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('import_contacts_from_vcard'),
                name = 'api_import_contacts_from_vcard'
            ),
        ]

    def get_last_contacted(self, request, **kwargs):
        '''
        pass limit, offset, owned (True by default, assigned,
        followed and include_activities with GET request
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
                {contact1_id: [activity1_id, activity2_id], contact2_id: [activity3_id]})
            '''
            obj_dict = {}
            obj_dict['contacts'] = self.get_bundle_list(contacts[0], request)
            obj_dict['activities'] = self.get_bundle_list(contacts[1], request)
            obj_dict['dict'] = contacts[2]
            return self.create_response(request, obj_dict)

    def get_cold_base(self, request, **kwargs):
        '''
        pass limit and offset  with GET request
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
        pass limit and offset through GET request
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
        pass limit and offset with GET request
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
        pass limit and offset with GET request
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
        Api implementation of search, pass search_params in this format:
        [('fn', 'startswith'), ('org__organization_unit', 'icontains'), 'bday']
        will search by the beginning of fn if search_params are not provided
        ast library f-n literal_eval converts the string representation of a
        list to a python list
        pass limit and offset through GET request
        '''
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        search_text = request.GET.get('search_text', '').encode('utf-8')
        search_params = ast.literal_eval(
            request.GET.get('search_params', "[('fn', 'startswith')]"))
        order_by = ast.literal_eval(request.GET.get('order_by', "[]"))
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
        Assigning a single contact with user
        '''
        user_id = int(request.GET.get('user_id',0))
        if not user_id:
            return self.create_response(
                    request, {'success':False, error_string:'User id is not set'}
                )
        contact_id = int(request.GET.get('contact_id',0))
        if not contact_id:
            return self.create_response(
                    request, {'success':False, error_string:'Contact id is not set'}
                )
        return self.create_response(
                request, {'success':Contact.assign_user_to_contact(user_id, contact_id)}
                )

    def assign_contacts(self, request, **kwargs):
        '''
        Assigning multiple contacts with user, send multiple contacts as so
        contact_ids=[1,2,3,4...n]
        '''
        import ast
        user_id = int(request.GET.get('user_id',0))
        if not user_id:
            return self.create_response(
                    request, {'success':False, error_string:'User id is not set'}
                )
        contact_ids = ast.literal_eval(request.GET.get('contact_ids',[]))
        if not contact_ids:
            return self.create_response(
                    request, {'success':False, error_string:'Contact ids are not set'}
                )
        return self.create_response(
                request, {'success':Contact.assign_user_to_contacts(user_id, contact_ids)}
                )

    def share_contact(self, request, **kwargs):
        ''' 
        Sharing a single contact with a single user
        '''
        share_to = int(request.GET.get('share_to',0))
        if not share_to:
            return self.create_response(
                request, {'success':False, 
                          'error_message':"You didn't specify with whom you want to share contact(s)"
                         }
                )
        share_from = int(request.GET.get('share_from',0))
        if not share_from:
            return self.create_response(
                request, {'success':False, 
                          'error_message':"You didn't specify the user whos sharing contact(s)"
                         }
                )
        contact_id = int(request.GET.get('contact_id',0))
        return self.create_response(
                request, {'success':Contact.share_contact(share_from, share_to, contact_id)}
            )

    def share_contacts(self, request, **kwargs):
        ''' 
        Sharing a single contact with a single user
        '''
        import ast
        share_to = int(request.GET.get('share_to',0))
        if not share_to:
            return self.create_response(
                request, {'success':False, 
                          'error_message':"You didn't specify with whom you want to share contact(s)"
                         }
                )
        share_from = int(request.GET.get('share_from',0))
        if not share_from:
            return self.create_response(
                request, {'success':False, 
                          'error_message':"You didn't specify the user whos sharing contact(s)"
                         }
                )
        contact_ids = ast.literal_eval(request.GET.get('contact_ids',[]))
        return self.create_response(
                request, {'success':Contact.share_contacts(share_from, share_to, contact_ids)}
            )

    def import_contacts_from_vcard(self, request, **kwargs):
        '''
        Import contact(s) from single vcard file
        '''
        if request.method == 'POST':
            print request.FILES['myfile']
            return self.create_response(
                    request, Contact.import_contacts_from_vcard(request.FILES['myfile'])
                )
        

class SalesCycleResource(CRMServiceModelResource):
    contact = fields.ForeignKey(ContactResource, 'contact')
    activities = fields.ToManyField(
        'alm_crm.api.ActivityResource', 'rel_activities',
        related_name='sales_cycle', null=True, full=True)
    products = fields.ToManyField(
        'alm_crm.api.ProductResource', 'products',
        related_name='sales_cycles', null=True, full=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource',
                              'owner', null=True, full=True)
    followers = fields.ToManyField('alm_crm.api.CRMUserResource',
                                   'followers', null=True, full=True)
    projected_value = fields.ToOneField('alm_crm.api.ValueResource',
                                        'projected_value', null=True,
                                        full=True)
    real_value = fields.ToOneField('alm_crm.api.ValueResource',
                                   'real_value', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = SalesCycle.objects.all()
        resource_name = 'sales_cycle'


class ActivityResource(CRMServiceModelResource):
    sales_cycle = fields.ForeignKey(SalesCycleResource, 'sales_cycle')
    feedback = fields.ToOneField('alm_crm.api.FeedbackResource',
                                 'activity_feedback', null=True, full=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource',
                              'activity_owner', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Activity.objects.all()
        resource_name = 'activity'


class ProductResource(CRMServiceModelResource):
    sales_cycles = fields.ToManyField(SalesCycleResource, 'sales_cycles')

    class Meta(CRMServiceModelResource.Meta):
        queryset = Product.objects.all()
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        resource_name = 'product'


class ValueResource(CRMServiceModelResource):

    class Meta(CRMServiceModelResource.Meta):
        queryset = Value.objects.all()
        resource_name = 'sales_cycle/value'


class CRMUserResource(CRMServiceModelResource):

    class Meta(CRMServiceModelResource.Meta):
        queryset = CRMUser.objects.all()
        resource_name = 'crmuser'


class ShareResource(CRMServiceModelResource):
    contact = fields.ForeignKey(ContactResource, 'contact',
                                full=True, null=True)
    share_to = fields.ForeignKey(CRMUserResource, 'share_to',
                                 full=True, null=True)
    share_from = fields.ForeignKey(CRMUserResource, 'share_from',
                                   full=True, null=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Share.objects.all()
        resource_name = 'share'

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


class FeedbackResource(CRMServiceModelResource):
    # activity = fields.OneToOneField(ActivityResource, 'feedback_activity', null=True, full=False)
    # value = fields.ToOneField(ValueResource, 'feedback_value', null=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Feedback.objects.all()
        resource_name = 'feedback'


class ContactListResource(CRMServiceModelResource):
    users = fields.ToManyField('alm_crm.api.CRMUserResource',
                                   'contact_list', null=True, full=True)

    class Meta(object):
        queryset = ContactList.objects.all()
        resource_name = 'contact_list'


        

            
