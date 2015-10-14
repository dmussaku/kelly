#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from almanet.url_resolvers import reverse_lazy as almanet_reverse_lazy
from django.contrib.auth.decorators import login_required
from django.conf import settings
from alm_company.models import Company
from alm_crm.models import Contact, ContactList, Share, SalesCycle
from alm_vcard.models import *
from alm_user.models import User
from .models import Service
from .forms import ServiceCreateForm, ReferralForm
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView, TemplateResponse
import kkb


class RedirectHomeView(RedirectView):

    def get(self, request, *a, **kw):
        return HttpResponseRedirect(
                almanet_reverse_lazy('user_login', subdomain=None))


# TODO: this needs to be deleted

class TestView1(TemplateView):

    def get_context_data(self, **kwargs):
        ctx = super(TestView1, self).get_context_data(**kwargs)
        ctx['subdomain'] = self.request.subdomain
        ctx['company'] = Company.objects.get(subdomain=self.request.subdomain)
        ctx['user'] = self.request.user
        return ctx


class TestView2(TemplateView):
    pass


def fork_index(request):
    if request.account.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        return HttpResponseRedirect(reverse_lazy('user_login'))


class ServiceList(ListView):

    model = Service
    queryset = Service.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super(ServiceList, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx


class ServiceCreateView(CreateView):
    form_class = ServiceCreateForm
    template_name = "almanet/service/service_create.html"
    success_url = reverse_lazy('service_list')


class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceCreateForm
    template_name = "almanet/service/service_update.html"
    success_url = reverse_lazy('service_list')


class ServiceDetailView(DetailView):
    model = Service
    template_name = "almanet/service/service_detail.html"


class ServiceDeleteView(DeleteView):
    model = Service
    template_name = "almanet/service/service_delete.html"
    success_url = reverse_lazy('service_list')


@login_required
def connect_service(request, slug, *args, **kwargs):
    try:
        service = Service.objects.get(slug=slug)
    except Service.DoesNotExist:
        raise Http404
    else:
        request.user.connect_service(service)
        if 'HTTP_REFERER' in request.META:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            subscr = request.user.get_subscr_by_service(service)
            return HttpResponseRedirect(subscr.backend.get_home_url())


@login_required
def disconnect_service(request, slug, *args, **kwargs):
    try:
        service = Service.objects.get(slug=slug)
    except Service.DoesNotExist:
        raise Http404
    else:
        request.user.disconnect_service(service)
        if 'HTTP_REFERER' in request.META:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            return HttpResponseRedirect(
                almanet_reverse_lazy('user_profile_url',
                                     subdomain=settings.MY_SD))

from django.views.decorators.csrf import csrf_exempt
from urlparse import parse_qs

def landing(request):
    template_name='index2.html'
    if request.method == 'POST':
        form = ReferralForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            url = reverse('user_registration')
            return HttpResponseRedirect(url+'?email='+email)
    else:
        form = ReferralForm()
    context = {
        'form': form,
    }
    return TemplateResponse(request, template_name, context)

        

@csrf_exempt
def landing_form(request):
    if request.method == 'POST':
        response = parse_qs(request.body, keep_blank_values=True)
        vcard = VCard(fn=response.get('fn')[0])
        vcard.save()
        if response.get('tel', None):
            tel = Tel(value=response.get('tel', None)[0], vcard=vcard, type='WORK')
            tel.save()
        if response.get('email', None):
            email = Email(value=response.get('email', None)[0], vcard=vcard, type='INTERNET')
            email.save()
        try:
            contact_list = ContactList.objects.get(title='С лэндинга')
        except:
            contact_list = ContactList(title='С лэндинга', subscription_id=4, owner_id=128)
            contact_list.save()
        c = Contact(subscription_id=4, vcard=vcard, owner_id=128)
        c.save()
        contact_list.add_contact(c.id)
        contact_list.save()
        share = Share(
                contact=c,
                share_to_id=128,
                share_from_id=128
                )
        if response.get('note', None):
            share.note=response.get('note', None)[0]
        else:
            share.note='Контакт созданный из формы лэндинга'
        share.save()
        SalesCycle.create_globalcycle(
            **{'subscription_id': c.subscription_id,
                     'owner_id': c.owner.id,
                     'contact_id': c.id
                    }
            )
        return HttpResponse('Cool')
    else:
        return HttpResponse('None')


def payment_view(request):
    if request.method == 'POST':
        print request.POST
    template_name='billing/input_payment.html'
    context = kkb.get_context(
        order_id = '333',amount="666",currency_id = "398") 
    print context
    return TemplateResponse(request, template_name, context)