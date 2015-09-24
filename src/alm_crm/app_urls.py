from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='crm/index.html'),
        name='crm_home'),

)
