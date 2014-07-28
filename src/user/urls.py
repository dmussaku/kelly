from django.conf.urls import patterns, url
from user.views import UserListView, UserProfileView, UserProfileSettings

from user.models import User

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
    	name='user_profile_settings_url')
)