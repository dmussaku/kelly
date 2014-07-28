from django.conf.urls import patterns, url
from user.views import UserListView, UserProfileView, user_profile_settings

from user.models import User

urlpatterns = patterns(
    '',
    url(r'^list/$', UserListView.as_view(
        model=User,
        template_name='user/user_list.html',
        queryset=User.objects.all())),
    url(r'^profile/$', UserProfileView.as_view(template_name='user/profile.html'), name='profile_url'),
    url(r'^profile/settings/$', user_profile_settings, {'template_name':'user/profile_settings.html'}, name='profile_settings_url')
)