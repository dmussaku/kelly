from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.views import login as django_login
from django.contrib.auth import views as contrib_auth_views

from alm_user.models import User
from alm_user.forms import UserPasswordSettingsForm
from alm_user.views import  UserListView, \
                            UserProfileView, \
                            UserProfileSettings,
                            UserRegistrationView, \
                            password_reset, \
                            user_login, \
                            user_logout

urlpatterns = patterns(
    '',
    url(r'^list/$', UserListView.as_view(
        model=User,
        template_name='user/user_list.html',
        queryset=User.objects.all()), name='user_list'),
    url(r'^profile/$', UserProfileView.as_view(
        template_name='user/profile.html'), 
        name='user_profile_url'),
    url(r'^profile/settings/$', UserProfileSettings.as_view(
        template_name='user/settings.html'),
        name='user_profile_settings_url'),
    url(r'^profile/settings/passwords$', contrib_auth_views.password_change, 
        {'password_change_form': UserPasswordSettingsForm,
         'post_change_redirect': reverse_lazy('user_profile_url'),
         'template_name':'user/settings_password.html'},
        name='user_profile_password_settings_url'),
    url(r'^registration/$', UserRegistrationView.as_view(),
        name='user_registration'),
    url(r'^login/$', user_login, name='user_login'),
    url(r'^dj/login/$',
        django_login, {
            'template_name': 'user/user_login.html'
        }, name='user_login'),
    url(r'^password_reset/$', password_reset, name='password_reset'),
    url(r'^logout/$', user_logout, name='user_logout'),
)