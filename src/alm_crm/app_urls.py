from django.conf.urls import patterns, url
from almanet.decorators import subdomain_required
from django.contrib.auth.decorators import login_required
from alm_crm.views import UserProductView
from almanet.models import Subscription

urlpatterns = patterns(
    '',
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', subdomain_required(
        login_required(UserProductView.as_view(
            model=Subscription,
            template_name='crm/dashboard.html'))),
        name='user_product_view'),
)
