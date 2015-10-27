from .models import (
    Plan,
    Payment,
    BankStatement,
    Subscription,
    )
from alm_company.models import Company
from tastypie import fields, http
from tastypie.authentication import (
    Authentication, 
    MultiAuthentication, 
    ApiKeyAuthentication, 
    BasicAuthentication,
    )
from django.conf.urls import url
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
import datetime
from datetime import timedelta
import kkb


class PlanResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get']
        queryset = Plan.objects.all()
        resource_name = 'plan'


class SubscriptionResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'patch']
        authentication = MultiAuthentication(
            SessionAuthentication(), 
            ApiKeyAuthentication(), 
            BasicAuthentication()
            )
        authorization = Authorization()
        queryset = Subscription.objects.all()
        resource_name = 'subscription'

class BankStatementResource(ModelResource):

    class Meta:
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        authentication = MultiAuthentication(
            SessionAuthentication(), 
            ApiKeyAuthentication(), 
            BasicAuthentication()
            )
        authorization = Authorization()
        queryset = BankStatement.objects.all()
        resource_name = 'bank_statement'

class PaymentResource(ModelResource):

    bank_statement = fields.ToOneField(
        'almanet.api.BankStatementResource', 'bank_statement', null=True, blank=True, readonly=True, full=True)

    class Meta:
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'patch']
        authentication = MultiAuthentication(
            SessionAuthentication(), 
            ApiKeyAuthentication(), 
            BasicAuthentication()
            )
        authorization = Authorization()
        queryset = Payment.objects.all()
        resource_name = 'payment'

    def full_dehydrate(self, bundle, for_list=False):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list)
        bundle.data['subscription_id'] = bundle.obj.subscription.id
        return bundle
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
                r"^(?P<resource_name>%s)/(?P<id>\d+)/get_epay_context%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_epay_context'),
                name='api_get_epay_context'
            ),
            url(
                r"^(?P<resource_name>%s)/change_plan%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_change_plan'),
                name='api_get_change_plan'
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



    def get_epay_context(self, request, **kwargs):
        id = kwargs.get('id')
        payment = Payment.objects.get(id=id)
        order_id = settings.PAYMENT_ID_PREFIX + str(id)
        amount = payment.amount
        currency_id = Payment.EPAY_CURRENCY_DICT[payment.currency]
        context = kkb.get_context(
            order_id=id , amount=str(amount), currency_id=currency_id)
        context = {'context':context}
        return self.create_response(request, context)

    def change_plan(self, request, **kwargs):
        data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        plan_id = data.get('plan_id',"")
        if not plan_id:
            return self.create_response(request, {'success':False})
        try:
            plan = Plan.objects.get(id=plan_id)
        except:
            return self.create_response(request, {'success':False})
        company = Company.objects.get(id=request.company.id)
        last_payment = company.subscription.payments.last()
        if not last_payment.status:
            last_payment.plan = plan
            if last_payment.currency == 'KZT':
                last_payment.amount = plan.price_kzt
            elif last_payment.currency == 'USD':
                last_payment.amount = plan.price_usd
            last_payment.save()
        else:
            today = datetime.datetime.now().date()
            t30 = last_payment.date_to_pay.date()
            t0 = last_payment.date_created.date()
            if last_payment.currency == 'KZT':
                amount2 = plan.price_kzt
            elif last_payment.currency == 'USD':
                amount2 = plan.price_usd
            amount1 = last_payment.amount
            new_amount = ((t30-today)/float(t30))*amount2 - amount1*(1-(today-t0)/float(t30))
            new_amount = round(new_amount)
            payment = Payment(
                amount=new_amount,
                currency=last_payment.currency,
                date_to_pay=last_payment.date_to_pay,
                plan=plan,
                subscription=company.subscription
                )
            payment.save()

        return self.create_response(request, PaymentResource().full_dehydrate(
                        PaymentResource().build_bundle(obj=payment, request=request) ))


    def get_epay_response(self, request, **kwargs):
        response = request.POST['response']
        id = kwargs.get('id')
        payment = Payment.objects.get(id=id)
        result = kkb.postlink(response)
        data = dict(
            (k.lower(), v) for k,v in result.data.iteritems()
            )
        if result.status:
            bank_statement = BankStatement(**data)
            bank_statement.save()
            payment.status = True
            payment.date_paid = datetime.datetime.now()
            payment.save()
        return HttpResponse(0)