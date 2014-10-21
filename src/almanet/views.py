from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from almanet.url_resolvers import reverse_lazy as almanet_reverse_lazy
from django.contrib.auth.decorators import login_required
from django.conf import settings
from alm_company.models import Company
from .models import Service
from .forms import ServiceCreateForm

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
    if request.user.is_authenticated():
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



















