from django.conf.urls import patterns, url
from user.views import 	UserListView, \
						UserProfileView, \
						UserProfileSettings
from django.contrib.auth import views as contrib_auth_views
from django.core.urlresolvers import reverse_lazy

from user.models import User
from user.forms import UserPasswordSettingsForm

urlpatterns = patterns(
    '',
    url(r'^list/$', UserListView.as_view(
        model=User,
        template_name='user/user_list.html',
        queryset=User.objects.all())),
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
    	name='user_profile_password_settings_url')
)