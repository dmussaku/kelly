from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.conf import settings
from alm_company.models import Company
from .models import Product
from alm_crm.models import Value
from .forms import ProductCreateForm, ValueCreateForm

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


class ProductCreateView(CreateView):
    form_class = ProductCreateForm
    template_name = "almanet/product/product_create.html"
    success_url = reverse_lazy('product_list')


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductCreateForm
    template_name = "almanet/product/product_update.html"
    success_url = reverse_lazy('product_list')


class ProductDetailView(DetailView):
    model = Product
    template_name = "almanet/product/product_detail.html"


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "almanet/product/product_delete.html"
    success_url = reverse_lazy('product_list')


class ValueList(ListView):

    model = Value
    queryset = Value.objects.all()


    def get_context_data(self, **kwargs):
        ctx = super(ValueList, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx


class ValueCreateView(CreateView):
    form_class = ValueCreateForm
    template_name = "almanet/value/value_create.html"
    success_url = reverse_lazy('value_list')


class ValueUpdateView(UpdateView):
    model = Value
    form_class = ValueCreateForm
    template_name = "almanet/value/value_update.html"
    success_url = reverse_lazy('value_list')


class ValueDetailView(DetailView):
    model = Value
    template_name = "almanet/value/value_detail.html"


class ValueDeleteView(DeleteView):
    model = Value
    template_name = "almanet/value/value_delete.html"
    success_url = reverse_lazy('value_list')


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



















