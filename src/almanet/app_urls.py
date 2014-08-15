from django.conf.urls import patterns, url, include
from utils.decorators import subdomain_required
from almanet.views import TestView1


urlpatterns = patterns(
    '',
    url(r'^crm/$', include('alm_crm.app_urls') ),
)
