from django.conf.urls import patterns, url
from almanet.url_resolvers import reverse_lazy
from .decorators import crmuser_required
from .views import DashboardView, FeedView, ContactDetailView, \
    ContactListView, ContactCreateView, ContactUpdateView, ActivityCreateView
from .models import Contact, Activity
from .forms import ContactForm, ActivityForm
from alm_vcard.views import import_vcard


# from almanet.models import Subscription

urlpatterns = patterns(
    '',
    url(r'^$', crmuser_required(
        DashboardView.as_view(
            # model=Subscription,
            template_name='crm/dashboard.html')),
        name='crm-dashboard'),
    url(r'^import_vcard/$', import_vcard, name='crm_import_vcard'),
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
    url(r'^contacts/create/$',
        crmuser_required(ContactCreateView.as_view(
            model=Contact,
            form_class=ContactForm,
            template_name="contact/contact_create.html",
            success_url=reverse_lazy('contacts_list'))),
        name='contact_create'),
    url(r'^contacts/update/(?P<pk>\d+)/$',
        crmuser_required(ContactUpdateView.as_view(
            model=Contact,
            form_clas=ContactForm,
            template_name="contact/contact_update.html",
            success_url=reverse_lazy('contact_list'))),
        name='contact_update'),

    url(r'^activities/create/$',
        crmuser_required(ActivityCreateView.as_view(
            model=Activity,
            form_class=ActivityForm,
            template_name='activity/activity_create.html',
            success_url=reverse_lazy('activity_list'))),
        name='activity_create'),
)
