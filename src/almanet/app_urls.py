from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from almanet.url_resolvers import reverse_lazy
from almanet.views import RedirectHomeView

from alm_user.api import UserResource, SessionResource
from alm_user.views import logout_view

from alm_crm import views

from alm_vcard import api as vcard_api

login_url = reverse_lazy('user_login', subdomain=None)


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'milestones', views.MilestoneViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', RedirectHomeView.as_view()),
    url(r'^(?P<service_slug>[-a-zA-Z0-9_]+)/', include('alm_crm.app_urls')),
    url(r'^api/v1/', include(router.urls, namespace='v1')),
    url(r'^auth/signout/$', logout_view, {'next_page': login_url},
        name='user_logout'),

)
