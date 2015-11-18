from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from alm_user.forms import UserPasswordSettingsForm
from alm_user.views import (
    UserProfileView, UserProfileSettings, UserServicesView,)
from django.contrib.auth import views as contrib_auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns(
    '',
    # url(r'^company/', include('alm_company.urls')),
    url(r'^services/$', login_required(UserServicesView.as_view(
        template_name='user/services.html')),
        name='user_services_url'),
    # TODO: temp, needs to be deleted
    url(r'^$', login_required(UserProfileView.as_view(
        template_name='user/profile.html')),
        name='user_profile_url'),
    url(r'^settings/$', login_required(UserProfileSettings.as_view(
        template_name='user/settings.html')),
        name='user_profile_settings_url'),
    url(r'^settings/passwords$', contrib_auth_views.password_change,
        {'password_change_form': UserPasswordSettingsForm,
         'post_change_redirect': reverse_lazy('user_profile_url'),
         'template_name': 'user/settings_password.html'},
        name='user_profile_password_settings_url'),
)
