from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from views import *

urlpatterns = patterns(
    '',
    url(r'^vcards/$', VCardListView.as_view(), name='vcard_list'),

    url(r'^vcards/export/(?P<id>\d+)/$', export_vcard, name='export_vcard'),
    
    url(r'^vcards/import/$', import_vcard, name='import_vcard'),

	url(r'^vcards/create/$', VCardCreateView.as_view(), name='vcard_create'),

	url(r'^vcards/update/(?P<pk>\d+)/$', VCardUpdateView.as_view(), name='vcard_update'),

	url(r'^tels/create/$', TelCreateView.as_view(), name='tel_create'),

	url(r'^tels/update/(?P<pk>\d+)/$', TelUpdateView.as_view(), name='tel_update'),

	url(r'^emails/create/$', EmailCreateView.as_view(), name='email_create'),

	url(r'^emails/update/(?P<pk>\d+)/$', EmailUpdateView.as_view(), name='email_update'),

	url(r'^geos/create/$', GeoCreateView.as_view(), name='geo_create'),

	url(r'^geos/update/(?P<pk>\d+)/$', GeoUpdateView.as_view(), name='geo_update'),

	url(r'^orgs/create/$', OrgCreateView.as_view(), name='org_create'),

	url(r'^orgs/update/(?P<pk>\d+)/$', OrgUpdateView.as_view(), name='org_update'),

	url(r'^adrs/create/$', AdrCreateView.as_view(), name='adr_create'),

	url(r'^adrs/update/(?P<pk>\d+)/$', AdrUpdateView.as_view(), name='adr_update'),

	url(r'^agents/create/$', AgentCreateView.as_view(), name='agent_create'),

	url(r'^agents/update/(?P<pk>\d+)/$', AgentUpdateView.as_view(), name='agent_update'),

	url(r'^categorys/create/$', CategoryCreateView.as_view(), name='category_create'),

	url(r'^categorys/update/(?P<pk>\d+)/$', CategoryUpdateView.as_view(), name='category_update'),

	url(r'^keys/create/$', KeyCreateView.as_view(), name='key_create'),

	url(r'^keys/update/(?P<pk>\d+)/$', KeyUpdateView.as_view(), name='key_update'),

	url(r'^labels/create/$', LabelCreateView.as_view(), name='label_create'),

	url(r'^labels/update/(?P<pk>\d+)/$', LabelUpdateView.as_view(), name='label_update'),

	url(r'^mailers/create/$', MailerCreateView.as_view(), name='mailer_create'),

	url(r'^mailers/update/(?P<pk>\d+)/$', MailerUpdateView.as_view(), name='mailer_update'),

	url(r'^nicknames/create/$', NicknameCreateView.as_view(), name='nickname_create'),

	url(r'^nicknames/update/(?P<pk>\d+)/$', NicknameUpdateView.as_view(), name='nickname_update'),

	url(r'^notes/create/$', NoteCreateView.as_view(), name='note_create'),

	url(r'^notes/update/(?P<pk>\d+)/$', NoteUpdateView.as_view(), name='note_update'),

	url(r'^roles/create/$', RoleCreateView.as_view(), name='role_create'),

	url(r'^roles/update/(?P<pk>\d+)/$', RoleUpdateView.as_view(), name='role_update'),

	url(r'^titles/create/$', TitleCreateView.as_view(), name='title_create'),

	url(r'^titles/update/(?P<pk>\d+)/$', TitleUpdateView.as_view(), name='title_update'),

	url(r'^tzs/create/$', TzCreateView.as_view(), name='tz_create'),

	url(r'^tzs/update/(?P<pk>\d+)/$', TzUpdateView.as_view(), name='tz_update'),

	url(r'^urls/create/$', UrlCreateView.as_view(), name='url_create'),

	url(r'^urls/update/(?P<pk>\d+)/$', UrlUpdateView.as_view(), name='url_update'),
	)
