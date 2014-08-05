from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from almanet.views import fork_index
from django.core.urlresolvers import reverse_lazy
from alm_user.forms import UserPasswordSettingsForm
from alm_user.views import UserProfileView, UserProfileSettings
from django.contrib.auth import views as contrib_auth_views
from django.contrib.auth.decorators import login_required


# from django.contrib import admin

# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^auth/', include('alm_user.urls')),
    url(r'^profile/$', login_required(UserProfileView.as_view(
        template_name='user/profile.html')),
        name='user_profile_url'),
    url(r'^profile/settings/$', login_required(UserProfileSettings.as_view(
        template_name='user/settings.html')),
        name='user_profile_settings_url'),
    url(r'^profile/settings/passwords$', contrib_auth_views.password_change,
        {'password_change_form': UserPasswordSettingsForm,
         'post_change_redirect': reverse_lazy('user_profile_url'),
         'template_name': 'user/settings_password.html'},
        name='user_profile_password_settings_url'),
    url(r'^$', fork_index),
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
