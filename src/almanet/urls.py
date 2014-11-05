from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from almanet.views import fork_index
from almanet.views import (
    ServiceList,
    connect_service,
    disconnect_service,
    ServiceCreateView,
    ServiceUpdateView,
    ServiceDeleteView,
    ServiceDetailView,
    )
from tastypie.api import Api
from alm_vcard.api import (
    VCardResource,
    VCardEmailResource,
    VCardTelResource,
    VCardOrgResource
    )
from alm_crm.api import ContactResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(VCardResource())
v1_api.register(VCardEmailResource())
v1_api.register(VCardTelResource())
v1_api.register(VCardOrgResource())
v1_api.register(ContactResource())


urlpatterns = patterns(
    '',
    url(r'^auth/', include('alm_user.urls')),
    # TODO: temp, needs to be deleted
    url(r'^crm/', include('alm_crm.urls')),
    url(r'^vcard/', include('alm_vcard.urls')),
    url(r'^services/$', ServiceList.as_view(
        template_name='almanet/service/service_list.html'),
        name='service_list'),

    url(r'^services/connect/(?P<slug>[-a-zA-Z0-9_]+)/$', connect_service,
        name='connect_service'),
    url(r'^services/disconnect/(?P<slug>[-a-zA-Z0-9_]+)/$', disconnect_service,
        name='disconnect_service'),
    url(r'^$', fork_index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^services/service_create/$', ServiceCreateView.as_view(), name='service_create'),
    url(r'^services/service_update/(?P<pk>\d+)/$', ServiceUpdateView.as_view(), name='service_update'),
    url(r'^services/service_detail/(?P<pk>\d+)/$', ServiceDetailView.as_view(), name='service_detail'),
    url(r'^services/service_delete/(?P<pk>\d+)/$', ServiceDeleteView.as_view(), name='service_delete'),
    url(r'^api/', include(v1_api.urls)),

)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:

    from mailviews.previews import autodiscover, site
    autodiscover()
    urlpatterns += patterns(
        '',
        url(r'^email-previews', view=site.urls))
