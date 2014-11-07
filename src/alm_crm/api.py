from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
from .models import Contact
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from alm_crm.models import (
    SalesCycle, 
    Activity, 
    Contact, 
    Share, 
    CRMUser, 
    Value,
    Feedback,
    )
from almanet.settings import DEFAULT_SERVICE

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

    def get_bundle_list(self,obj_list,request):
        '''
        receives a queryset and returns a list of bundles
        '''
        objects=[]
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
    vcard = fields.ToOneField('alm_vcard.api.VCardResource','vcard', null=True, full=True)
    sales_cycles = fields.ToManyField(
        'alm_crm.api.SalesCycleResource', 'sales_cycles',
        related_name='contact', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Contact.objects.all()
        resource_name = 'contact'

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/recent%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_contacted'),
                name = 'api_last_contacted'
            ),
            url(
                r"^(?P<resource_name>%s)/cold_base%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_cold_base'),
                name = 'api_cold_base'
            ),
            url(
                r"^(?P<resource_name>%s)/leads%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_leads'),
                name = 'api_leads'
            ),
            url(
                r"^(?P<resource_name>%s)/search%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('search'),
                name = 'api_search'
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
        contacts = Contact().get_contacts_by_last_activity_date(
            user_id=request.user.id, 
            include_activities=include_activities,
            owned=owned,
            assigned=assigned,
            followed=followed, 
            limit=limit, 
            offset=offset)
        if not include_activities:
            return self.create_response(
                    request, {'objects':self.get_bundle_list(contacts, request)}
                )
        else:
            '''
            returns 
                (Queryset<Contact>, 
                Queryset<Activity>, 
                {contact1_id: [activity1_id, activity2_id], contact2_id: [activity3_id]})
            '''
            obj_dict={}
            obj_dict['contacts'] = self.get_bundle_list(contacts[0], request)
            obj_dict['activities'] = self.get_bundle_list(contacts[1], request)
            obj_dict['dict'] = contacts[2]
            return self.create_response(request, obj_dict) 

    def get_cold_base(self, request, **kwargs):
        '''
        pass limit and offset  with GET request
        '''
        limit = int(request.GET.get('limit',20))
        offset = int(request.GET.get('offset',0))
        contacts = Contact().get_cold_base(limit, offset)
        return self.create_response(
                request, {'objects':self.get_bundle_list(contacts,request)}
            )

    def get_leads(self, request, **kwargs):
        '''
        pass limit and offset through GET request
        '''
        STATUS_LEAD = 1
        limit = int(request.GET.get('limit',20))
        offset = int(request.GET.get('offset',0))
        contacts = Contact().get_contacts_by_status(STATUS_LEAD, limit, offset)
        return self.create_response(
                request, {'objects':self.get_bundle_list(contacts,request)}
            )

    def search(self, request, **kwargs):
        '''
        Api implementation of search, pass search_params in this format:
        [('fn', 'startswith'), ('org__organization_unit', 'icontains'), 'bday']
        will search by the beginning of fn if search_params are not provided
        ast library f-n literal_eval converts the string representation of a
        list to a python list
        pass limit and offset through GET request
        '''
        import ast
        limit = int(request.GET.get('limit',20))
        offset = int(request.GET.get('offset',0))
        search_text = request.GET.get('search_text','').encode('utf-8')
        search_params = ast.literal_eval(
            request.GET.get('search_params',"[('fn', 'startswith')]"))
        contacts = Contact().filter_contacts_by_vcard(
            search_text=search_text,
            search_params=search_params,
            limit=limit,
            offset=offset)
        return self.create_response(
                request, {'objects':self.get_bundle_list(contacts,request)}
            )


class SalesCycleResource(CRMServiceModelResource):
    contact = fields.ForeignKey(ContactResource, 'contact')
    activities = fields.ToManyField(
        'alm_crm.api.ActivityResource', 'rel_activities',
        related_name='sales_cycle', null=True, full=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'rel_owner', null=True, full=True)
    followers = fields.ToManyField('alm_crm.api.CRMUserResource', 'rel_followers', null=True, full=True)
    projected_value = fields.ToOneField('alm_crm.api.ValueResource', 'projected_value', null=True, full=True)
    real_value = fields.ToOneField('alm_crm.api.ValueResource', 'real_value', null=True, full=True)
    class Meta(CRMServiceModelResource.Meta):
        queryset = SalesCycle.objects.all()
        resource_name = 'sales_cycle'


class ActivityResource(CRMServiceModelResource):
    sales_cycle = fields.ForeignKey(SalesCycleResource, 'sales_cycle')
    feedback = fields.ToOneField('alm_crm.api.FeedbackResource', 'activity_feedback', null=True, full=True)
    owner = fields.ToOneField('alm_crm.api.CRMUserResource', 'activity_owner', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Activity.objects.all()
        resource_name = 'activity'


class ValueResource(CRMServiceModelResource):

    class Meta(CRMServiceModelResource.Meta):
        queryset = Value.objects.all()
        resource_name = 'sales_cycle/value'


class CRMUserResource(CRMServiceModelResource):

    class Meta(CRMServiceModelResource.Meta):
        queryset = CRMUser.objects.all()
        resource_name = 'crmuser'


class ShareResource(CRMServiceModelResource):
    contact = fields.ForeignKey(ContactResource, 'contact', full=True, null=True)
    share_to = fields.ForeignKey(ContactResource, 'contact', full=True, null=True)
    share_from = fields.ForeignKey(ContactResource, 'contact', full=True, null=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Share.objects.all()
        resource_name = 'share'

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/recent%s$" % 
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_shares'),
                name = 'api_last_shares'
            ),
        ]

    def get_last_shares(self, request, **kwargs):
        '''
        pass limit and offset  with GET request
        '''
        limit = int(request.GET.get('limit',20))
        offset = int(request.GET.get('offset',0))
        shares = Share().get_shares(limit=limit, offset=offset)
        return self.create_response(
                request, {'objects':self.get_bundle_list(shares, request)}
            )

class FeedbackResource(CRMServiceModelResource):
    # activity = fields.OneToOneField(ActivityResource, 'feedback_activity', null=True, full=False)
    # value = fields.ToOneField(ValueResource, 'feedback_value', null=True)
    
    class Meta(CRMServiceModelResource.Meta):
        queryset = Feedback.objects.all()
        resource_name = 'feedback'
