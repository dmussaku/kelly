from django.conf.urls import patterns, url, include
from almanet.url_resolvers import reverse_lazy
from django.views.generic.base import TemplateView

from alm_user.views import logout_view

login_url = reverse_lazy('user_login', subdomain=None)


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='crm/index.html'),
        name='crm_home'),
    url(r'^auth/signout/$', logout_view, {'next_page': login_url},
        name='user_logout'),

)
