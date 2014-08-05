from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from alm_company.views import CompanySettingsView


urlpatterns = patterns(
    '',
    url(r'^settings/$', CompanySettingsView.as_view(
        template_name='company/settings.html'),
        name='user_company_settings_url'),
    
)

