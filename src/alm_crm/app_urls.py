from django.conf.urls import patterns, url
from almanet.decorators import subdomain_required
from django.contrib.auth.decorators import login_required
from alm_crm.views import UserProductView

urlpatterns = patterns(
    '',
    url(r'^(?P<slug>[\w-]+)/$', subdomain_required(
        login_required(UserProductView.as_view())),
        name='user_product_view'),
)
