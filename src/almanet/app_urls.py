from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from almanet.url_resolvers import reverse_lazy
from almanet.views import RedirectHomeView

from alm_user.api import UserResource, SessionResource
from alm_user.views import logout_view

from alm_crm.apii import (
    activities,
    app_state,
    contacts,
    contact_lists,
    custom_fields,
    hashtags,
    milestones,
    product_groups,
    products,
    reports,
    sales_cycles,
    shares,
    filters,
    attached_files,
    comments,
)

from alm_user.apii import users

from alm_vcard import api as vcard_api

login_url = reverse_lazy('user_login', subdomain=None)

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
    AttachedFileResource,
    )
from alm_user.api import UserResource, SessionResource
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
v1_api.register(SessionResource())
v1_api.register(AttachedFileResource())

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'activity', activities.ActivityViewSet, 'activity')
router.register(r'app_state', app_state.AppStateViewSet, 'app_state')
router.register(r'contact', contacts.ContactViewSet, 'contact')
router.register(r'contact_list', contact_lists.ContactListViewSet, 'contact_list')
router.register(r'custom_field', custom_fields.CustomFieldViewSet, 'custom_field')
router.register(r'hashtag', hashtags.HashTagViewSet, 'hashtag')
router.register(r'milestone', milestones.MilestoneViewSet, 'milestone')
router.register(r'product', products.ProductViewSet, 'product')
router.register(r'product_group', product_groups.ProductGroupViewSet, 'product_group')
router.register(r'report', reports.ReportViewSet, 'report')
router.register(r'sales_cycle', sales_cycles.SalesCycleViewSet, 'sales_cycle')
router.register(r'share', shares.ShareViewSet, 'share')
router.register(r'filter', filters.FilterViewSet, 'filter')
router.register(r'user', users.UserViewSet, 'user')
router.register(r'attached_file', attached_files.AttachedFileViewSet, 'attached_file')
router.register(r'comment', comments.CommentViewSet, 'comment')

urlpatterns = patterns(
    '',
    url(r'^$', RedirectHomeView.as_view()),
    url(r'^(?P<service_slug>[-a-zA-Z0-9_]+)/', include('alm_crm.app_urls')),
    url(r'^api/v1/', include(router.urls, namespace='v1')),
    url(r'^api/', include(v1_api.urls)),
    url(r'^auth/signout/$', logout_view, {'next_page': login_url},
        name='user_logout'),

)
