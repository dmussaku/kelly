from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
# from django.contrib import admin


# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^auth/', include('user.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
