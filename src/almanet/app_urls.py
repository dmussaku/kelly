from django.conf.urls import patterns, url, include
from .views import RedirectHomeView

urlpatterns = patterns(
    '',
    url(r'^$', RedirectHomeView.as_view()),
    url(r'^(?P<service_slug>[-a-zA-Z0-9_]+)/', include('alm_crm.app_urls')),
)
