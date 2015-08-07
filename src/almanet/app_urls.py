from django.conf.urls import patterns, url, include
from .views import RedirectHomeView


from tastypie.api import Api
from alm_vcard import api as vcard_api
from alm_crm.api import (
    ContactResource,
    SalesCycleResource,
    MilestoneResource,
    ActivityResource,
    ProductResource,
    ProductGroupResource,
    ShareResource,
    CRMUserResource,
    ValueResource,
    ContactListResource,
    ConstantsResource,
    AppStateResource,
    MobileStateResource,
    SalesCycleProductStatResource,
    FilterResource,
    CommentResource,
    CustomSectionResource,
    CustomFieldResource,
    CustomFieldValueResource,
    ReportResource,
    HashTagReferenceResource,
    )
from alm_user.api import UserResource
from tastypie.resources import ModelResource


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
v1_api.register(ProductGroupResource())
v1_api.register(ShareResource())
v1_api.register(ValueResource())
v1_api.register(CRMUserResource())
v1_api.register(UserResource())
v1_api.register(ContactListResource())
v1_api.register(AppStateResource())
v1_api.register(MobileStateResource())
v1_api.register(ConstantsResource())
v1_api.register(SalesCycleProductStatResource())
v1_api.register(FilterResource())
v1_api.register(CommentResource())
v1_api.register(CustomSectionResource())
v1_api.register(CustomFieldResource())
v1_api.register(CustomFieldValueResource())
v1_api.register(MilestoneResource())
v1_api.register(ReportResource())
v1_api.register(HashTagReferenceResource())

urlpatterns = patterns(
    '',
    url(r'^$', RedirectHomeView.as_view()),
    url(r'^(?P<service_slug>[-a-zA-Z0-9_]+)/', include('alm_crm.app_urls')),
    url(r'^api/', include(v1_api.urls)),

)
