from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from alm_contact.views import ContactListView, ContactCreateView, ContactUpdateView, ContactDetailView

urlpatterns = patterns(
	'',
	url(r'^$', ContactListView.as_view(), name='contact_list'),
	url(r'^create/$', ContactCreateView.as_view(), name='contact_create'),
	url(r'^update/(?P<pk>\d+)/$', ContactUpdateView.as_view(), name='contact_update'), 
	url(r'^(?P<pk>\d+)/$', ContactDetailView.as_view(), name='contact_detail'), 
)