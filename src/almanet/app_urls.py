from django.conf.urls import patterns, url
from utils.decorators import subdomain_required
from almanet.views import TestView1


urlpatterns = patterns(
    '',
    url(r'^crm/$', subdomain_required(
        TestView1.as_view(template_name='almanet/crm.html'))),
)
