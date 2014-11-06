from tastypie.resources import ModelResource
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from tastypie import fields
from alm_crm.models import SalesCycle, Activity, Contact, Product
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

    class Meta:
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication())
        authorization = Authorization()


class ContactResource(CRMServiceModelResource):
    sales_cycles = fields.ToManyField(
        'alm_crm.api.SalesCycleResource', 'sales_cycles',
        related_name='contact', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = Contact.objects.all()
        resource_name = 'contact'


class SalesCycleResource(CRMServiceModelResource):
    contact = fields.ForeignKey(ContactResource, 'contact')
    activities = fields.ToManyField(
        'alm_crm.api.ActivityResource', 'rel_activities',
        related_name='sales_cycle', null=True, full=True)
    products = fields.ToManyField(
        'alm_crm.api.ProductResource', 'products',
        related_name='sales_cycles', null=True, full=True)

    class Meta(CRMServiceModelResource.Meta):
        queryset = SalesCycle.objects.all()
        resource_name = 'sales_cycle'


class ActivityResource(CRMServiceModelResource):
    sales_cycle = fields.ForeignKey(SalesCycleResource, 'sales_cycle')

    class Meta(CRMServiceModelResource.Meta):
        queryset = Activity.objects.all()
        resource_name = 'activity'


class ProductResource(CRMServiceModelResource):
    sales_cycles = fields.ToManyField(SalesCycleResource, 'sales_cycles')

    class Meta(CRMServiceModelResource.Meta):
        queryset = Product.objects.all()
        resource_name = 'product'
