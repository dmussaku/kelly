from django.views.generic import TemplateView, ListView
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.conf import settings
from alm_company.models import Company
from .models import Product

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


class ProductList(ListView):

    model = Product
    queryset = Product.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super(ProductList, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx


@login_required
def connect_product(request, slug, *args, **kwargs):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        raise Http404
    else:
        request.user.connect_product(product)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def disconnect_product(request, slug, *args, **kwargs):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        raise Http404
    else:
        request.user.disconnect_product(product)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
