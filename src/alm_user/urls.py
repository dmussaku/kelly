from django.conf.urls import patterns, url
from alm_user.views import UserListView, UserRegistrationView, password_reset, user_login, user_logout
from alm_user.models import User
from django.contrib.auth.views import login as django_login

urlpatterns = patterns(
    '',
    url(r'^list/$', UserListView.as_view(
        model=User,
        template_name='user/user_list.html',
        queryset=User.objects.all()), name='user_list'),
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
