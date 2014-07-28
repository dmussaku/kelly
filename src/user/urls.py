from django.conf.urls import patterns, url
from user.views import UserListView
from user.models import User

urlpatterns = patterns(
    '',
    url(r'^list/$', UserListView.as_view(
        model=User,
        template_name='user/user_list.html',
        queryset=User.objects.all())))
