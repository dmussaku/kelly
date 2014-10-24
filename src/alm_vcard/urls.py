from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from views import *

urlpatterns = patterns(
    '',
    url(r'^vcards/$', VCardListView.as_view(), name='vcard_list'),
    
    url(r'^$', VCardListView.as_view(), name='vcard_list_view'),

    url(r'^vcards/(?P<pk>\d+)/$', VCardDetailView.as_view(), name='vcard_detail'),

    # url(r'^vcards/export/(?P<id>\d+)/$', export_vcard, name='export_vcard'),
    
    # url(r'^vcards/import/$', import_vcard, name='import_vcard'),

	url(r'^vcards/create/$', VCardCreateView.as_view(), name='vcard_create'),

	url(r'^vcards/update/(?P<pk>\d+)/$', VCardUpdateView.as_view(), name='vcard_update'),

	url(r'^tels/create/$', TelCreateView.as_view(), name='tel_create'),

	url(r'^tels/$', VCardListView.as_view(), name='tel_list'),

	url(r'^tels/(?P<pk>\d+)/$', TelDetailView.as_view(), name='tel_detail'),

	url(r'^tels/update/(?P<id>\d+)/$', TelUpdateView.as_view(), name='tel_update'),

	url(r'^emails/create/$', EmailCreateView.as_view(), name='email_create'),

	url(r'^emails/$', VCardListView.as_view(), name='email_list'),

	url(r'^emails/(?P<pk>\d+)/$', EmailDetailView.as_view(), name='email_detail'),

	url(r'^emails/update/(?P<id>\d+)/$', EmailUpdateView.as_view(), name='email_update'),

	url(r'^orgs/create/$', OrgCreateView.as_view(), name='org_create'),

	url(r'^orgs/$', VCardListView.as_view(), name='org_list'),

	url(r'^orgs/(?P<pk>\d+)/$', OrgDetailView.as_view(), name='org_detail'),

	url(r'^orgs/update/(?P<id>\d+)/$', OrgUpdateView.as_view(), name='org_update'),

	url(r'^geos/create/(?P<pk>\d+)/$', GeoCreateView.as_view(), name='geo_create'),

	url(r'^geos/update/(?P<id>\d+)/$', GeoUpdateView.as_view(), name='geo_update'),



	url(r'^orgs/update/(?P<id>\d+)/$', OrgUpdateView.as_view(), name='org_update'),

	url(r'^adrs/create/(?P<pk>\d+)/$', AdrCreateView.as_view(), name='adr_create'),

	url(r'^adrs/update/(?P<id>\d+)/$', AdrUpdateView.as_view(), name='adr_update'),

	url(r'^agents/create/(?P<pk>\d+)/$', AgentCreateView.as_view(), name='agent_create'),

	url(r'^agents/update/(?P<id>\d+)/$', AgentUpdateView.as_view(), name='agent_update'),

	url(r'^categorys/create/(?P<pk>\d+)/$', CategoryCreateView.as_view(), name='category_create'),

	url(r'^categorys/update/(?P<id>\d+)/$', CategoryUpdateView.as_view(), name='category_update'),

	url(r'^keys/create/(?P<pk>\d+)/$', KeyCreateView.as_view(), name='key_create'),

	url(r'^keys/update/(?P<id>\d+)/$', KeyUpdateView.as_view(), name='key_update'),

	url(r'^labels/create/(?P<pk>\d+)/$', LabelCreateView.as_view(), name='label_create'),

	url(r'^labels/update/(?P<id>\d+)/$', LabelUpdateView.as_view(), name='label_update'),

	url(r'^mailers/create/(?P<pk>\d+)/$', MailerCreateView.as_view(), name='mailer_create'),

	url(r'^mailers/update/(?P<id>\d+)/$', MailerUpdateView.as_view(), name='mailer_update'),

	url(r'^nicknames/create/(?P<pk>\d+)/$', NicknameCreateView.as_view(), name='nickname_create'),

	url(r'^nicknames/update/(?P<id>\d+)/$', NicknameUpdateView.as_view(), name='nickname_update'),

	url(r'^notes/create/(?P<pk>\d+)/$', NoteCreateView.as_view(), name='note_create'),

	url(r'^notes/update/(?P<id>\d+)/$', NoteUpdateView.as_view(), name='note_update'),

	url(r'^roles/create/(?P<pk>\d+)/$', RoleCreateView.as_view(), name='role_create'),

	url(r'^roles/update/(?P<id>\d+)/$', RoleUpdateView.as_view(), name='role_update'),

	url(r'^titles/create/(?P<pk>\d+)/$', TitleCreateView.as_view(), name='title_create'),

	url(r'^titles/update/(?P<id>\d+)/$', TitleUpdateView.as_view(), name='title_update'),

	url(r'^tzs/create/(?P<pk>\d+)/$', TzCreateView.as_view(), name='tz_create'),

	url(r'^tzs/update/(?P<id>\d+)/$', TzUpdateView.as_view(), name='tz_update'),

	url(r'^urls/create/(?P<pk>\d+)/$', UrlCreateView.as_view(), name='url_create'),

	url(r'^urls/update/(?P<id>\d+)/$', UrlUpdateView.as_view(), name='url_update'),
	)
