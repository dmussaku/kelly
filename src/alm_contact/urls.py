from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from alm_contact.views import ContactListView, ContactCreateView, ContactUpdateView, ContactDetailView
from models import Contact

urlpatterns = patterns(
	'',
	url(r'^$', ContactListView.as_view(
			queryset = Contact.objects.all(),
			context_object_name="contacts",
			template_name = "contact/contact_list.html",
		), name='contact_list'
	),
	url(r'^excerpt/$', ContactListView.as_view(
			queryset = Contact.objects.all(),
			context_object_name="contacts",
			template_name = "contact/contact_list_excerpt.html",
		), name='contact_list_excerpt'
	),
	url(r'^recent/$', ContactListView.as_view(
			queryset = Contact.objects.order_by("-date_created"),
			context_object_name="contacts",
			template_name = "contact/contact_list.html",
		), name='contact_list_by_date_created'
	),
	url(r'^recent/excerpt/$', ContactListView.as_view(
			queryset = Contact.objects.order_by("-date_created"),
			context_object_name="contacts",
			template_name = "contact/contact_list_excerpt.html",
		), name='contact_list_by_date_created_excerpt'
	),
	url(r'^create/$', ContactCreateView.as_view(), name='contact_create'),
	url(r'^update/(?P<pk>\d+)/$', ContactUpdateView.as_view(), name='contact_update'), 
	url(r'^(?P<pk>\d+)/$', ContactDetailView.as_view(), name='contact_detail'), 
)