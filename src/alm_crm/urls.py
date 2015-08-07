from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from views import (
    # DashBoardTemplateView,
    FeedView,
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDetailView,
    ContactDeleteView,
    ContactAddMentionView,
    SalesCycleListView,
    SalesCycleCreateView,
    SalesCycleUpdateView,
    SalesCycleAddMentionView,
    SalesCycleDetailView,
    SalesCycleDeleteView,
    ActivityCreateView,
    ActivityListView,
    ActivityDetailView,
    ActivityUpdateView,
    ActivityDeleteView,
    CommentCreateView,
    CommentListView,
    CommentAddMentionView,
    ValueListView,
    ValueCreateView,
    ValueUpdateView,
    ValueDetailView,
    ValueDeleteView,

    contact_export
    )
from models import Contact, SalesCycle, Activity, Comment

urlpatterns = patterns(
    '',
    url(r'^contacts/excerpt/$', ContactListView.as_view(
            queryset = Contact.objects.all(),
            context_object_name="contacts",
            template_name = "contact/contact_list_excerpt.html",
        ), name='contact_list_excerpt'
    ),
    url(r'^contacts/recent/$', ContactListView.as_view(
            queryset = Contact.objects.order_by("-date_created"),
            context_object_name="contacts",
            template_name = "contact/contact_list.html",
        ), name='contact_list_by_date_created'
    ),
    url(r'^contacts/recent/excerpt/$', ContactListView.as_view(
            queryset = Contact.objects.order_by("-date_created"),
            context_object_name="contacts",
            template_name = "contact/contact_list_excerpt.html",
        ), name='contact_list_by_date_created_excerpt'
    ),
    url(r'^vcard/(?P<pk>\d+)/$', contact_export, name='contact_export'),
    url(r'^vcard/(?P<pk>\d+)/(?P<format>(vcf|web)?)/$', contact_export, name='contact_export'),
    url(r'^contacts/delete/(?P<pk>\d+)/$', ContactDeleteView.as_view(), name='contact_delete'),
    url(r'^contacts/add_mention/(?P<pk>\d+)/$', ContactAddMentionView.as_view(), name='contact_add_mention'),

    url(r'^sales_cycles/$', SalesCycleListView.as_view(
            queryset = SalesCycle.objects.all(),
            context_object_name="sales_cycles",
            template_name = "sales_cycle/sales_cycle_list.html",
        ), name='sales_cycle_list'
    ),
    url(r'^sales_cycles/recent/$', SalesCycleListView.as_view(
            queryset = SalesCycle.objects.order_by("-date_created"),
            context_object_name="sales_cycles",
            template_name = "sales_cycles/sales_cycles_list.html",
        ), name='sales_cycle_list_by_date_created'
    ),
    url(r'^sales_cycles/create/$', SalesCycleCreateView.as_view(), name='sales_cycle_create'),
    url(r'^sales_cycles/update/(?P<pk>\d+)/$', SalesCycleUpdateView.as_view(), name='sales_cycle_update'),
    url(r'^sales_cycles/add_mention/(?P<pk>\d+)/$', SalesCycleAddMentionView.as_view(), name='sales_cycle_add_mention'),
    url(r'^sales_cycles/delete/(?P<pk>\d+)/$', SalesCycleDeleteView.as_view(), name='sales_cycle_delete'),

    url(r'^activities/create/$', ActivityCreateView.as_view(), name='activity_create'),
    url(r'^activities/$', ActivityListView.as_view(), name='activity_list'),
    url(r'^activities/(?P<pk>\d+)/$', ActivityDetailView.as_view(), name='activity_detail'),
    url(r'^activities/update/(?P<pk>\d+)/$', ActivityUpdateView.as_view(), name='activity_update'),
    url(r'^activities/delete/(?P<pk>\d+)/$', ActivityDeleteView.as_view(), name='activity_delete'),

    url(r'^comments/$', CommentListView.as_view(
            queryset = Comment.objects.all(),
            context_object_name="comments",
            template_name = "comment/comment_list.html",
        ), name='comment_list'
    ),
    url(r'^comments/create/$', CommentCreateView.as_view(), name='comment_create'),
    url(r'^comments/add_mention/(?P<pk>\d+)/$', CommentAddMentionView.as_view(), name='comment_add_mention'),

    url(r'^values/$', ValueListView.as_view(
        template_name='value/value_list.html'),
        name='value_list'),
    url(r'^values/value_create/$', ValueCreateView.as_view(), name='value_create'),
    url(r'^values/value_update/(?P<pk>\d+)/$', ValueUpdateView.as_view(), name='value_update'),
    url(r'^values/value_detail/(?P<pk>\d+)/$', ValueDetailView.as_view(), name='value_detail'),
    url(r'^values/value_delete/(?P<pk>\d+)/$', ValueDeleteView.as_view(), name='value_delete'),

)
