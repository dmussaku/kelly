from django.conf.urls import patterns, url, include
from alm_vcard.views import import_vcard

from .decorators import crmuser_required
from .models import Contact, Activity, Share, Comment
from .forms import (
    ContactForm,
    SalesCycleForm,
    ActivityForm,
    ShareForm,
    CommentForm
    )
from .views import (
    DashboardView,
    FeedView,
    ProfileView,

    ContactDetailView,
    ContactListView,
    ContactCreateView,
    ContactUpdateView,

    ActivityCreateView,
    ActivityDetailView,

    SalesCycleCreateView,
    sales_cycle_value_update,
    sales_cycle_add_mention,
    sales_cycle_add_product,
    sales_cycle_remove_product,

    ShareCreateView,
    ShareListView,

    CommentCreateView,
    comment_create_view,
    comment_delete_view,
    comment_edit_view,
    ContactSearchListView,
    contact_create_view,
    )

urlpatterns = patterns(
    '',
    url(r'^$', crmuser_required(
        DashboardView.as_view()),
        name='crm_home'),
    url(r'^feed/$', crmuser_required(
        FeedView.as_view(template_name='crm/feed.html')),
        name='feed'),
    url(r'^profile/$', crmuser_required(
        ProfileView.as_view(template_name='crm/profile.html')),
        name='profile'),
    url(r'^import_vcard/$', import_vcard, name='crm_import_vcard'),

    
    url(r'^comments/(?P<content_type>[\w]+)/(?P<object_id>[\d]+)/$',
        crmuser_required(comment_create_view),
        name='comments'),

    url(r'^comments/delete/$',
        crmuser_required(comment_delete_view),
        name='comment_delete'
        ),
    url(r'^comments/edit/$',
        crmuser_required(comment_edit_view),
        name='comment_edit'
        ),

    url(r'^contacts/search/$',
        ContactSearchListView.as_view(
            model=Contact,
            template_name='crm/contacts/contact_search.html',
            ),
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
    url(r'^contacts/update/(?P<contact_pk>[\d]+)/$',
        crmuser_required(ContactUpdateView.as_view(
            model=Contact,
            template_name='crm/contacts/contact_update.html',
            pk_url_kwarg='contact_pk')),
        name='contact_update'),
    url(r'^contacts/create/$',
        crmuser_required(contact_create_view),
        name='contact_create'),
    url(r'^vcards/', include('alm_vcard.urls')),
    url(r'^contacts/update/(?P<pk>\d+)/$',
        crmuser_required(ContactUpdateView.as_view(
            model=Contact,
            form_class=ContactForm,
            template_name="contact/contact_update.html")),
        name='contact_update'),
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
    url(r'^activities/create/$',
        crmuser_required(ActivityCreateView.as_view(
            model=Activity,
            form_class=ActivityForm,
            template_name='activity/activity_create.html')),
        name='activity_create'),
    url(r'^activities/(?P<pk>[\d]+)/$',
        ActivityDetailView.as_view(
            model=Activity,
            template_name='crm/activity.html'
            ),
        name='activity_detail'),

    url(r'^sales_cycles/create/$',
        crmuser_required(SalesCycleCreateView.as_view(
            form_class=SalesCycleForm,
            template_name='sales_cycle/sales_cycle_create.html')),
        name='sales_cycle_create'),
    url(r'^sales_cycle/(?P<sales_cycle_pk>[\d]+)/value/update/$',
        crmuser_required(sales_cycle_value_update),
        name='sales_cycle_value_update'),
    url(r'^sales_cycle/(?P<sales_cycle_pk>[\d]+)/mentions/add/$',
        crmuser_required(sales_cycle_add_mention),
        name='sales_cycle_add_mention'),
    url(r'^sales_cycle/(?P<sales_cycle_pk>[\d]+)/products/add/$',
        crmuser_required(sales_cycle_add_product),
        name='sales_cycle_add_product'),
    url(r'^sales_cycle/(?P<sales_cycle_pk>[\d]+)/products/remove/$',
        crmuser_required(sales_cycle_remove_product),
        name='sales_cycle_remove_product'),

    
)
