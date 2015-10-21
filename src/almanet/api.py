from .models import (
    Plan,
    Payment,
    BankStatement,
    )
from alm_company.models import Company
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
from django.conf import settings
import kkb


class PlanResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get']
        queryset = Plan.objects.all()
        resource_name='plan'

    def dehydrate(self, bundle):
        bundle = super(self.__class__, self).dehydrate(bundle)
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
                r"^(?P<resource_name>%s)/(?P<id>\d+)/epay_response%s$" %
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

    '''
    Example of a template form that should be submitted:
    <form name="SendOrder" method="post" action="https://testpay.kkb.kz/jsp/process/logon.jsp">
        <input type="hidden" name="Signed_Order_B64" value="{{ context }}">
        E-mail: <input type="text" name="email" size=50 maxlength=50  value="test@tes.kz">
       
       <input type="hidden" name="Language" value="eng">
        <input type="hidden" name="BackLink" value="http://178.88.64.83:80/payment/">
        <input type="hidden" name="PostLink" value="http://178.88.64.83:80/payment_post/">
        <button class="login-submit" type="submit">{{ _("Pay") }}</button>
    </form>

    Where action always sends post data to kkb link, there are test ones and live ones
    context is the thing that gets created by our api function get_payment_process. There are
    also BackLinks and PostLinks - those are the ones that should change 
    '''

    def get_payment_process(self, request, **kwargs):
        id = kwargs.get('id')
        payment = Payment.objects.get(id=id)
        order_id = settings.PAYMENT_ID_PREFIX + str(id)
        amount = payment.amount
        currency_id = Payment.EPAY_CURRENCY_DICT[payment.currency]
        context = kkb.get_context(
            order_id=id , amount=str(amount), currency_id=currency_id)
        context = {'context':context}
        return self.create_response(request, context)

    def get_epay_response(self, request, **kwargs):
        response = request.POST['response']
        id = kwargs.get('id')
        payment = Payment.objects.get(id=id)
        result = kkb.postlink(response)
        if result.status:
            bank_statement = BankStatement(**result.data)
            bank_statement.save()
        return HttpResponse(0)