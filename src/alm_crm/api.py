from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie import fields
from alm_crm.models import SalesCycle, Activity


class SalesCycleResource(ModelResource):
    activities = fields.ToManyField(
        'alm_crm.api.ActivityResource', 'rel_activities',
        related_name='activities', null=True, full=True)

    class Meta:
        queryset = SalesCycle.objects.all()
        resource_name = 'sales_cycle'
        authentication = BasicAuthentication()
        authorization = Authorization()


class ActivityResource(ModelResource):
    sales_cycle = fields.ForeignKey(SalesCycleResource, 'sales_cycle')

    class Meta:
        queryset = Activity.objects.all()
        resource_name = 'sales_cycle/activity'
        authentication = BasicAuthentication()
        authorization = Authorization()
