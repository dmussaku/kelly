from django.views.generic import ListView
from django.views.generic.base import TemplateView, TemplateResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
# from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.conf import settings
from almanet.settings import MY_SD

from alm_user.models import User, Referral
from alm_user.forms import(
    RegistrationForm, 
    UserBaseSettingsForm, 
    UserPasswordSettingsForm, 
    ReferralForm, 
    PasswordResetForm,
) 
from almanet.models import Service
from almanet.url_resolvers import reverse_lazy

# for testing, need to be deleted
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from almanet.url_resolvers import reverse as almanet_reverse

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
            if request.user:
                subscr = request.user.get_subscriptions()[0]
                print subscr.get_home_url()
                if not subscr is None:
                    return HttpResponseRedirect(subscr.get_home_url())
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


class UserListView(ListView):

    def get_context_data(self, **kwargs):
        return super(UserListView, self).get_context_data(**kwargs)


class UserRegistrationView(CreateView):

    form_class = RegistrationForm
    success_url = reverse_lazy('user_profile_url', subdomain=settings.MY_SD)
    template_name = 'user/user_registration.html'

@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, user_pk=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert user_pk is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse_lazy('password_reset_complete')
    else:
        post_reset_redirect = reverse_lazy('password_reset_success')

    try:
        user = User._default_manager.get(pk=user_pk)
    except User.DoesNotExist:
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


def password_reset_success(request,
                        template_name='registration/password_reset_success.html',
                        current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


class UserProfileView(TemplateView):
    """
    Shows users profile info
    """

    def get_context_data(self, **kwargs):
        ctx = super(UserProfileView, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        ctx['company'] = self.request.user.get_owned_company()
        ctx['time'] = datetime.now()  # for testing, need to be deleted
        return ctx


class UserProfileSettings(UpdateView):
    """
    Profile settings base view
    """

    model = User
    form_class = UserBaseSettingsForm
    success_url = reverse_lazy('user_profile_url', subdomain=settings.MY_SD)

    def get_object(self, **kwargs):
        return self.request.user


class UserServicesView(ListView):

    model = Service

    def get_context_data(self, **kwargs):
        ctx = super(UserServicesView, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx

    def get_queryset(self, *args, **kwargs):
        queryset = self.request.user.connected_services()
        return queryset


def referral(request, template_name='user/login-registration.html',
          referral_form=ReferralForm):
    if request.method == "POST":
        if request.META.get('HTTP_REFERER',''):
            data = request.POST.copy()
            data['referer'] = request.META.get('HTTP_REFERER')
            form = referral_form(request, data=data)
        else:
            form = referral_form(request, data=request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('referral_complete'))
    else:
        form = referral_form(request)

    context = {
        'form': form
    }
    return TemplateResponse(request, template_name, context)


def referral_complete(request, template_name='user/referral-complete.html'):
    return TemplateResponse(request, template_name)
