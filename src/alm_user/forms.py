from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from alm_user.models import Account, User, Referral
from alm_user.emails import (
    UserResetPasswordEmail, 
    UserRegistrationEmail,
    SubdomainForgotEmail,
    )
from alm_company.models import Company
import re

# need to finish validation errors for the passwords form


class RegistrationForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)
    company_name = forms.CharField(max_length=200)
    company_subdomain = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput(),
                               max_length=100)

    def clean_email(self):
        email = self.cleaned_data['email']
        if email in [user.email for user in User.objects.all()]:
            raise forms.ValidationError( _("Email %s is already registered") % email)
        return email

    def clean_company_subdomain(self):
        company_subdomain = self.cleaned_data['company_subdomain']
        if company_subdomain in settings.BUSY_SUBDOMAINS:
            busy_subdomains = ', '.join(settings.BUSY_SUBDOMAINS)
            raise forms.ValidationError(_(
                "The following company names are busy: %(names)s") % {
                'names': busy_subdomains})
        if company_subdomain in [company.subdomain for company in Company.objects.all()]:
            raise forms.ValidationError( _("Subdomain is already taken") )
        if not re.match('\w', company_subdomain):
            raise forms.ValidationError( 
                _("Subdomain must be written in latin alphabet letters") 
                )
        return company_subdomain

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        if not password:
            raise forms.ValidationError( 
                _("Enter valid password") 
                )
        return password

    def save(self, commit=True):
        user = User(email=self.cleaned_data['email'])
        user.set_password(self.cleaned_data['password'])
        if commit:
            gened_subdomain = Company.generate_subdomain(
                self.cleaned_data['company_subdomain'])
            company = Company(
                name=self.cleaned_data['company_name'],
                subdomain=gened_subdomain)
            company.save()
            user.save()
            account = Account(
                company=company,
                user=user,
                is_supervisor=True
                )
            account.save()
            mail_context = {
                'site_name': settings.SITE_NAME,
                'gu__user__email': user.email,
            }
            UserRegistrationEmail(**mail_context).send(
                to=(user.email,),
                bcc=settings.BCC_EMAILS)
        return user

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            print self.user_cache
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                accounts = self.user_cache.accounts.all()
                if len(accounts) == 1 and not accounts[0].is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
        return self.cleaned_data

    def check_for_test_cookie(self):
        warnings.warn("check_for_test_cookie is deprecated; ensure your login "
                "view is CSRF-protected.", DeprecationWarning)

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form):
    # subdomain = forms.CharField(label=_("Subdomain"), max_length=254)
    email = forms.EmailField(label=_("Email"), max_length=254)
    error_messages = (_("Account with such email is not registered."))

    def clean_email(self):
        email = self.cleaned_data['email']
        # subdomain = self.cleaned_data['subdomain']
        try:
            self.cached_user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(self.error_messages[0])
        else:
            return email

    def save(self, domain_override=None,
             subject_template_name=None,
             email_template_name=None,
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        # from django.core.mail import send_mail
        mail_context = {
            'site_name': settings.SITE_NAME,
            'gu__user__email': self.cached_user.email,
            'token': token_generator.make_token(self.cached_user),
            'protocol': 'https' if use_https else 'http',
        }
        UserResetPasswordEmail(**mail_context).send(
            to=(self.cached_user.email,),
            bcc=settings.BCC_EMAILS)


class UserBaseSettingsForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'timezone']


class UserPasswordSettingsForm(forms.Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput, label=_("Old password"))
    password = forms.CharField(
        widget=forms.PasswordInput(), label=_('New Password'))
    password2 = forms.CharField(
        widget=forms.PasswordInput(), label=_('Repeat your password'))

    error_messages = {
        'password_mismatch': _("New passwords are not equal"),
        'old_password_incorrect': _("Enter valid old password.")
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserPasswordSettingsForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not check_password(old_password, self.user.password):
            raise forms.ValidationError(
                self.error_messages['old_password_incorrect'])
        return old_password

    def clean(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password and password2:
            if password != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'])
        return self.cleaned_data

    def save(self, *args, **kwargs):
        self.user.set_password(self.cleaned_data['password'])
        self.user.save()
        return self.user


class ReferralForm(ModelForm):

    class Meta:
        model = Referral

    def __init__(self, request=None, *args, **kwargs):
        if kwargs.get('data', None):
            self.referer = kwargs['data'].get('referer', None)

        self.request = request
        super(self.__class__, self).__init__(*args, **kwargs)
