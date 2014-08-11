from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from almanet.views import fork_index
from almanet.views import (
    TestView2,
    ProductList,
    connect_product,
    disconnect_product)

urlpatterns = patterns(
    '',
    url(r'^auth/', include('alm_user.urls')),
    # TODO: temp, needs to be deleted
    url(r'^crm/$', TestView2.as_view(template_name='almanet/about_crm.html')),
    url(r'^products/$', ProductList.as_view(
        template_name='almanet/product_list.html'),
        name='product_list'),
    url(r'^products/connect/(?P<slug>\w+)/$', connect_product,
        name='connect_product'),
    url(r'^products/disconnect/(?P<slug>\w+)/$', disconnect_product,
        name='disconnect_product'),
    url(r'^$', fork_index),
    url(r'^contacts/', include('alm_contact.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:

    from mailviews.previews import autodiscover, site
    autodiscover()
    urlpatterns += patterns(
        '',
        url(r'^email-previews', view=site.urls))
