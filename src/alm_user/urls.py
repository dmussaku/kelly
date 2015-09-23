from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.views import (
    password_reset as django_password_reset,
    password_reset_done as django_password_reset_done,)

from alm_user.forms import PasswordResetForm, SubdomainForgotForm
# from alm_user.views import UserListView, UserRegistrationView 
from alm_user.views import (
    login_view, 
    password_reset_confirm, 
    referral, 
    referral_complete, 
    password_reset_success,
    subdomain_forgot,
    ChooseSubdomain
    )
from alm_user.models import User
from django.views.generic import TemplateView

login_url = reverse_lazy('user_login')

urlpatterns = patterns(
    '',
    url(r'^signin/$',
        login_view, {'template_name': 'user/user_login.html'},
        name='user_login'),

    url(r'^signin/company/$',
        ChooseSubdomain.as_view(template_name='user/choose_subdomain.html'),
        name='choose_subdomain'),

    url(r'^referral/$',
        referral, {'template_name': 'user/login-register.html'},
        name='user_referral'),

    url(r'^referral/complete/$', referral_complete, {'template_name': 'user/referral-complete.html'}, 
        name='referral_complete'),

    url(r'^password-reset/$', 
        django_password_reset, {
        'template_name': 'user/password_reset.html',
        'password_reset_form': PasswordResetForm,
        'email_template_name': 'emails/password_reset_email.txt',
        'subject_template_name': 'emails/password_reset_subject.txt',
        }, name='password_reset'),

    url(r'^password-reset/done/$', 
        django_password_reset_done, {
        'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^password-reset/subdomain_forgot/$', 
        subdomain_forgot, {
        'template_name': 'user/subdomain_forgot.html'},
        name='subdomain_forgot'),

    url(r'^password-reset/subdomain_forgot/done/$', 
        django_password_reset_done, {
        'template_name': 'user/subdomain_forgot_done.html'},
        name='subdomain_forgot_done'),

    url(r'^password-reset/success/$', 
        password_reset_success, {
        'template_name': 'user/password_reset_success.html'},
        name='password_reset_success'),

    url(r'^reset/(?P<user_pk>[\d]+)/(?P<token>.*)/$',
        password_reset_confirm,
        {'template_name': 'user/password_reset_confirm.html',
         'post_reset_redirect': 'user_login'},
        name='password_reset_confirm'),
)

