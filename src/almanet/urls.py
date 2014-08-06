from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

# from django.contrib import admin

# TODO: delete this
from almanet.views import TestView2

# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^auth/', include('alm_user.urls')),
    url(r'^profile/company/', include('alm_company.urls')),
    url(r'^crm/$', TestView2.as_view(template_name='almanet/about_crm.html')),
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
