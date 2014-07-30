from django.conf.urls import patterns, url
from alm_user.views import UserListView
from alm_user.models import User

urlpatterns = patterns(
    '',
    url(r'^list/$', UserListView.as_view(
        model=User,
        template_name='user/user_list.html',
        queryset=User.objects.all())))
