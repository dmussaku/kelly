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
    RedirectHomeView,
    landing_form
    )
from django.views.generic import TemplateView


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', RedirectHomeView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
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
    url(r'api/doc/', include('tastypie_swagger.urls', namespace='tastypie_swagger')),
    url(r'agreement/$', TemplateView.as_view(template_name='almanet/agreement.crm.html'), name='agreement'),
    url(r'landing_form/$', landing_form, name='landing_form'),

)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:

    from mailviews.previews import autodiscover, site
    autodiscover()
    urlpatterns += patterns(
        '',
        url(r'^email-previews', view=site.urls))


if settings.USE_PROFILER:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
