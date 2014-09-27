from django.conf.urls import patterns, url
from .decorators import crmuser_required
from .views import DashboardView, ContactDetailView
from .models import Contact
from almanet.models import Subscription

urlpatterns = patterns(
    '',
    url(r'^$', crmuser_required(
        DashboardView.as_view(
            # model=Subscription,
            template_name='crm/dashboard.html')),
        name='crm-dashboard'),
    url(r'^contacts/(?P<contact_pk>[\d]+)/$',
        ContactDetailView.as_view(
            model=Contact,
            template_name='crm/contacts/contact_detail.html',
            pk_url_kwarg='contact_pk'),
        name='crm-contacts'),
)
