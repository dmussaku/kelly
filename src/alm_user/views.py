from django.views.generic import ListView
from django.views.generic.base import TemplateView, TemplateResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
# from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.conf import settings
from almanet.settings import MY_SD

from alm_company.models import Company
from alm_user.models import User, Referral, Account
from alm_user.forms import(
    # RegistrationForm,
    UserBaseSettingsForm,
    UserPasswordSettingsForm,
    ReferralForm,
    PasswordResetForm,
    AuthenticationForm,
    RegistrationForm,
)
# from alm_user.auth_backend import login, logout
from almanet.models import Service
from almanet.url_resolvers import reverse_lazy

# for testing, need to be deleted
from datetime import datetime
# from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.sites.models import get_current_site
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from almanet.url_resolvers import reverse as almanet_reverse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import SuspiciousOperation



@sensitive_post_parameters()
@csrf_protect
@never_cache
def login_view(request, template_name='registration/login.html',
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
            login(request, form.get_user())

            accounts = request.user.accounts.all()
            if len(accounts) > 1:
                return HttpResponseRedirect(
                    reverse_lazy('choose_subdomain')
                )
            return HttpResponseRedirect(
                reverse_lazy('crm_home',
                        subdomain=accounts[0].company.subdomain,
                        kwargs={'service_slug': settings.DEFAULT_SERVICE}))
    else:
        form = authentication_form(request)
    comps = request.COOKIES.get('comps', None)
    logged_in_companies = []
    if request.user and not request.user.is_anonymous():
        logged_in_companies = [account.company for account in request.user.accounts.all()]
    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'logged_in_companies': logged_in_companies
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def logout_view(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None, **kwargs):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    return HttpResponseRedirect('/auth/signin')

@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


class UserListView(ListView):

    def get_context_data(self, **kwargs):
        return super(UserListView, self).get_context_data(**kwargs)

'''
class UserRegistrationView(CreateView):

    form_class = RegistrationForm
    success_url = reverse_lazy('user_profile_url', subdomain=settings.MY_SD)
    template_name = 'user/user_registration.html'
'''

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
        user = User.objects.get(pk=user_pk)
        print user
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

def registration(request, template_name='user/registration.html',
    registration_form=RegistrationForm):
    if request.method == "POST":
        form = registration_form(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            accounts = request.user.accounts.all()
            if len(accounts) > 1:
                return HttpResponseRedirect(
                    reverse_lazy('choose_subdomain')
                )
            return HttpResponseRedirect(
                reverse_lazy('crm_home',
                        subdomain=accounts[0].company.subdomain,
                        kwargs={'service_slug': settings.DEFAULT_SERVICE}))
            # return HttpResponseRedirect(reverse_lazy('user_registration_success'))
    else:
        email = request.GET.get('email','')
        form = registration_form(initial={"email":email})
    context = {
        'form': form
    }
    return TemplateResponse(request, template_name, context)


def referral_complete(request, template_name='user/referral-complete.html'):
    return TemplateResponse(request, template_name)


class ChooseSubdomain(TemplateView):

    def get_context_data(self, **kwargs):
        ctx = super(ChooseSubdomain, self).get_context_data(**kwargs)
        accounts = self.request.user.accounts.all()
        ctx['companies'] = [account.company for account in accounts]
        return ctx



class ActivationView(TemplateView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.

    """


class ActivationView(TemplateView):
    """
    Base class for user activation views.

    """
    template_name = 'registration/activate.html'

    def get(self, *args, **kwargs):
        """
        The base activation logic; subclasses should leave this method
        alone and implement activate(), which is called from this
        method.
        """

        try:
            activated_user = self.activate(*args, **kwargs)
        except SuspiciousOperation as e:
            # raise 403 error if activation key expired or already used
            return HttpResponseForbidden()

        if activated_user:
            # signals.user_activated.send(sender=self.__class__,
            #                             user=activated_user,
            #                             request=self.request)
            success_url = self.get_success_url(activated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return super(ActivationView, self).get(*args, **kwargs)

    def activate(self, *args, **kwargs):
        # This is safe even if, somehow, there's no activation key,
        # because unsign() will raise BadSignature rather than
        # TypeError on a value of None.
        username, subdomain = self.validate_key(kwargs.get('activation_key'))
        if username is not None:
            account = self.get_account(username, subdomain)
            if account is not None:
                if account.was_actived:
                    raise SuspiciousOperation('Activation Key already used')
                account.was_actived = True
                account.is_active = True
                account.save()
                return account.user
        return None

    def get_success_url(self, user):
        if user.has_usable_password():
            return ('user_login', (), {})
        else:
            print 'has no password', user
            # authorize user
            # redirect to password setting form
            return ('set_password', (), {})

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or ``None`` if not.

        """
        signer = signing.TimestampSigner(salt=settings.REGISTRATION_SALT)
        try:
            protected_key_struct = signer.unsign(
                activation_key,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            key_struct = signing.loads(protected_key_struct)
            return key_struct.get('username'), key_struct.get('subdomain')
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.BadSignature:
            return None

    def get_account(self, username, subdomain):
        """
        Given the verified username, look up and return the
        corresponding user account if it exists, or ``None`` if it
        doesn't.

        """
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            account = user.accounts.get(company__subdomain=subdomain)
            return account
        except User.DoesNotExist:
            return None
        except Account.DoesNotExist:
            return None
