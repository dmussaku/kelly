from django.conf.urls import patterns, url

from almanet.url_resolvers import reverse_lazy
from .decorators import crmuser_required
from .views import DashboardView, FeedView, ContactDetailView, \
    ContactListView, ContactCreateView, ContactUpdateView, ActivityCreateView,\
    SalesCycleCreateView, ShareCreateView, ShareListView
from alm_vcard.views import import_vcard
from .models import Contact, Activity, Share
from .forms import ContactForm, ActivityForm, SalesCycleForm, ShareForm

from .models import Comment
from .forms import CommentForm
from almanet.url_resolvers import reverse as almanet_reverse
from .decorators import crmuser_required
from alm_vcard.views import import_vcard
from .views import (
    DashboardView,
    ContactDetailView,
    ContactListView,
    FeedView,
    ActivityDetailView,
    CommentCreateView,
    comment_delete_view,
    contact_search,
    )
from .models import Contact, Activity


# from almanet.models import Subscription

urlpatterns = patterns(
    '',
    url(r'^$', crmuser_required(
        DashboardView.as_view()),
        name='crm_home'),
    url(r'^import_vcard/$', import_vcard, name='crm_import_vcard'),
    url(r'^feed/$', crmuser_required(
        FeedView.as_view(template_name='crm/feed.html')),
        name='feed'),

    url(r'^comments/delete/(?P<comment_id>[\d]+)/$',
        crmuser_required(comment_delete_view),
        name='comment_delete'
        ),

    url(r'^comments/(?P<content_type>[\w]+)/(?P<object_id>[\d]+)/$',
        crmuser_required(CommentCreateView.as_view(
            model = Comment,
            form_class = CommentForm,
            template_name = 'comment/comment_create.html')),
        name='comments'),

    url(r'^contacts/search/(?P<query_string>[-a-zA-Z0-9_]+)/$',
        contact_search,
        name='contact-search'),

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
            template_name="contact/contact_create.html")),
        name='contact_create'),
    url(r'^contacts/update/(?P<pk>\d+)/$',
        crmuser_required(ContactUpdateView.as_view(
            model=Contact,
            form_class=ContactForm,
            template_name="contact/contact_update.html")),
        name='contact_update'),

    url(r'^activities/create/$',
        crmuser_required(ActivityCreateView.as_view(
            model=Activity,
            form_class=ActivityForm,
            template_name='activity/activity_create.html')),
        name='activity_create'),

    url(r'^sales_cycles/create/$',
        crmuser_required(SalesCycleCreateView.as_view(
            form_class=SalesCycleForm,
            template_name='sales_cycle/sales_cycle_create.html')),
        name='sales_cycle_create'),

    url(r'^share/create/$',
        crmuser_required(ShareCreateView.as_view(
            form_class=ShareForm,
            template_name='crm/share/share_create.html')),
        name='share_create'),
    url(r'^share/$',
        crmuser_required(ShareListView.as_view(
            model=Share,
            template_name='crm/share/share_list.html')),
        name='share_list'),
    url(r'^activities/(?P<pk>[\d]+)/$',
            ActivityDetailView.as_view(
                model=Activity,
                template_name='crm/activity.html'
                ),
            name = 'activity_detail'
        ),
)
