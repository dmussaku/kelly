from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from alm_user.public_api import users

router = DefaultRouter()
router.register(r'user', users.UserViewSet, 'user')

urlpatterns = patterns(
    '',
    url(r'^api/v1/', include(router.urls, namespace='v1')),
)
