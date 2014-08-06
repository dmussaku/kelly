from django.conf.urls import patterns, include, url

from almanet.views import TestView1


urlpatterns = patterns(
    '',
    url(r'^crm/$', TestView1.as_view(template_name='almanet/crm.html')),
)