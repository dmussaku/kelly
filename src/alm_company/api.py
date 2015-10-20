from .models import (
    Company,
    Plan,
    Payment,
    BankStatement,
    )
from tastypie import fields, http
from tastypie.authentication import (
    Authentication, 
    MultiAuthentication, 
    ApiKeyAuthentication, 
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.exceptions import ImmediateHttpResponse, NotFound, Unauthorized
from tastypie.resources import Resource, ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from alm_crm.api import CRMServiceModelResource
from almanet.utils.api import RequestContext, SessionAuthentication
import kkb


class PlanResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get']
        queryset = Plan.objects.all()
        resource_name='plan'

    def dehydrate(self, bundle):
        bundle = super(self.__class__, self).dehydrate(bundle)
        bundle.data['companies'] = [company.id for company in bundle.obj.companies.all()]
        return bundle


class PaymentResource(CRMServiceModelResource):

    class Meta:
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        authentication = MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication(), BasicAuthentication())
        authorization = Authorization()
        queryset = Payment.objects.all()
        resource_name='payment'


    '''
    test cards, any name can be entered:
    4405645000006150    09-2025     653

    5483185000000293    09-2025     343

    377514500009951     09-2025     3446
    '''
    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/epay_response%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_epay_response'),
                name='api_get_epay_response'
                ),
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/pay%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('payment_process'),
                name='payment_process'
            ),
        ]

    def get_payment_process(self, request, **kwargs):
        

    def get_epay_response(self, request, **kwargs):
        response = request.POST['response']
        result = kkb.postlink(response)
        if result.status:
            bank_statement = BankStatement(**result.data)
            bank_statement.save()
        return HttpResponse(0)