from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from almanet.views import fork_index
from almanet.views import (
    ServiceList,
    connect_service,
    disconnect_service,
    ServiceCreateView,
    ServiceUpdateView,
    ServiceDeleteView,
    ServiceDetailView,
    RedirectHomeView
    )
from tastypie.api import Api
from alm_vcard import api as vcard_api
from alm_crm.api import (
    ContactResource,
    SalesCycleResource,
    ActivityResource,
    ProductResource,
    ShareResource,
    FeedbackResource,
    CRMUserResource,
    ValueResource,
    ContactListResource,
    AppStateResource,
    SalesCycleProductStatResource,
    FilterResource,
    CommentResource
    )
from alm_user.api import UserSessionResource, UserResource
from tastypie.resources import ModelResource
from django.views.generic.base import TemplateView

admin.autodiscover()
v1_api = Api(api_name='v1')
for obj in vars(vcard_api).values():
    try:
        if (issubclass(obj, ModelResource) and obj != ModelResource):
            v1_api.register(obj())
    except:
        pass
v1_api.register(ContactResource())
v1_api.register(SalesCycleResource())
v1_api.register(ActivityResource())
v1_api.register(ProductResource())
v1_api.register(ShareResource())
v1_api.register(ValueResource())
v1_api.register(FeedbackResource())
v1_api.register(CRMUserResource())
v1_api.register(UserSessionResource())
v1_api.register(UserResource())
v1_api.register(ContactListResource())
v1_api.register(AppStateResource())
v1_api.register(SalesCycleProductStatResource())
v1_api.register(FilterResource())
v1_api.register(CommentResource())


urlpatterns = patterns(
    '',
    url(r'^$', RedirectHomeView.as_view()),
    url(r'^auth/', include('alm_user.urls')),
    # TODO: temp, needs to be deleted
    url(r'^crm/', include('alm_crm.urls')),
    url(r'^vcard/', include('alm_vcard.urls')),
    url(r'^services/$', ServiceList.as_view(
        template_name='almanet/service/service_list.html'),
        name='service_list'),

    url(r'^services/connect/(?P<slug>[-a-zA-Z0-9_]+)/$', connect_service,
        name='connect_service'),
    url(r'^services/disconnect/(?P<slug>[-a-zA-Z0-9_]+)/$', disconnect_service,
        name='disconnect_service'),
    url(r'^$', fork_index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^services/service_create/$', ServiceCreateView.as_view(), name='service_create'),
    url(r'^services/service_update/(?P<pk>\d+)/$', ServiceUpdateView.as_view(), name='service_update'),
    url(r'^services/service_detail/(?P<pk>\d+)/$', ServiceDetailView.as_view(), name='service_detail'),
    url(r'^services/service_delete/(?P<pk>\d+)/$', ServiceDeleteView.as_view(), name='service_delete'),
    url(r'^api/', include(v1_api.urls)),
    url(r'api/doc/', include('tastypie_swagger.urls', namespace='tastypie_swagger')),

)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:

    from mailviews.previews import autodiscover, site
    autodiscover()
    urlpatterns += patterns(
        '',
        url(r'^email-previews', view=site.urls))
