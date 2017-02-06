from django.conf.urls import patterns, url, include
from tastypie.api import Api
from alm_user.api import UserResource

v1_api = Api(api_name='v1')
# v1_api.register(SessionResource())
v1_api.register(UserResource())


urlpatterns = patterns(
    '',
    url(r'', include(v1_api.urls)),
)
