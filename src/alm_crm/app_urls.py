from django.conf.urls import patterns, url
from .decorators import crmuser_required
from .views import DashboardView, ContactDetailView, ContactListView, FeedView, ActivityDetailView
from .models import Contact, Activity
# from almanet.models import Subscription

urlpatterns = patterns(
    '',
    url(r'^$', crmuser_required(
        DashboardView.as_view(
            # model=Subscription,
            template_name='crm/dashboard.html')),
        name='crm-dashboard'),
    url(r'^feed/$', crmuser_required(
        FeedView.as_view(template_name='crm/feed.html')),
        name='feed'),

    url(r'^contacts/$',
        crmuser_required(ContactListView.as_view(
            model=Contact,
            template_name='crm/contacts/contact_list.html',
        )), name='contacts_list'),
    url(r'^contacts/(?P<contact_pk>[\d]+)/$',
        crmuser_required(ContactDetailView.as_view(
            model=Contact,
            template_name='crm/contacts/contact_detail.html',
            pk_url_kwarg='contact_pk')),
        name='contact_detail'),
    url(r'^activities/(?P<pk>[\d]+)/$', 
            ActivityDetailView.as_view(
                model=Activity,
                template_name='crm/activity.html'
                ),
            name = 'activity_detail'
        ),
)
