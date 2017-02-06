from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', login_required(TemplateView.as_view(template_name='crm/index.html')),
        name='crm_home'),

)
