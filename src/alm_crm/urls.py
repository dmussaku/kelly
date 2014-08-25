from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from views import (
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDetailView,
    ContactDeleteView,
    GoalListView,
    GoalCreateView,
    GoalUpdateView,
    GoalDetailView,
    GoalDeleteView,
    contact_export
    )
from models import Contact, Goal

urlpatterns = patterns(
    '',
    url(r'^contacts/$', ContactListView.as_view(
            queryset = Contact.objects.all(),
            context_object_name="contacts",
            template_name = "contact/contact_list.html",
        ), name='contact_list'
    ),
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
    url(r'^contacts/create/$', ContactCreateView.as_view(), name='contact_create'),
    url(r'^contacts/update/(?P<pk>\d+)/$', ContactUpdateView.as_view(), name='contact_update'),
    url(r'^vcard/(?P<pk>\d+)/$', contact_export, name='contact_export'),
    url(r'^vcard/(?P<pk>\d+)/(?P<format>(vcf|web)?)/$', contact_export, name='contact_export'),
    url(r'^contacts/(?P<pk>\d+)/$', ContactDetailView.as_view(), name='contact_detail'),
    url(r'^contacts/delete/(?P<pk>\d+)/$', ContactDeleteView.as_view(), name='contact_delete'),

    url(r'^goals/$', GoalListView.as_view(
            queryset = Goal.objects.all(),
            context_object_name="goals",
            template_name = "goal/goal_list.html",
        ), name='goal_list'
    ),
    url(r'^goals/recent/$', GoalListView.as_view(
            queryset = Goal.objects.order_by("-date_created"),
            context_object_name="goals",
            template_name = "goals/goals_list.html",
        ), name='goal_list_by_date_created'
    ),
    url(r'^goals/create/$', GoalCreateView.as_view(), name='goal_create'),
    url(r'^goals/update/(?P<pk>\d+)/$', GoalUpdateView.as_view(), name='goal_update'),
    url(r'^goals/(?P<pk>\d+)/$', GoalDetailView.as_view(), name='goal_detail'),
    url(r'^goals/delete/(?P<pk>\d+)/$', GoalDeleteView.as_view(), name='goal_delete'),
)
