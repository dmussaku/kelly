from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    '',
    url(r'^(?P<service_slug>[-a-zA-Z0-9_]+)/', include('alm_crm.app_urls')),
)
