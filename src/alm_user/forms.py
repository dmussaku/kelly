from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from alm_user.models import User, Referral
from alm_user.emails import UserResetPasswordEmail, UserRegistrationEmail
from alm_company.models import Company

# need to finish validation errors for the passwords form


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(),
                               max_length=100)
    confirm_password = forms.CharField(widget=forms.PasswordInput(),
                                       max_length=100)
    company_name = forms.CharField(max_length=100)

    class Meta:

        model = User
        fields = ['first_name', 'last_name', 'email', 'timezone']

    def clean_company_name(self):
        company_name = self.cleaned_data['company_name']
        if company_name in settings.BUSY_SUBDOMAINS:
            busy_subdomains = ', '.join(settings.BUSY_SUBDOMAINS)
            raise forms.ValidationError(_(
                "The following company names are busy: %(names)s") % {
                'names': busy_subdomains})
        return company_name

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        if (not password):
            return super(RegistrationForm, self).clean()
        if (not confirm_password):
            return super(RegistrationForm, self).clean()
        if (password != confirm_password):
            raise forms.ValidationError('Password Mismatch')
        else:
            return super(RegistrationForm, self).clean()

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=commit)
        user.set_password(self.cleaned_data['password'])
        if commit:
            gened_subdomain = Company.generate_subdomain(
                self.cleaned_data['company_name'])
            company = Company(
                name=self.cleaned_data['company_name'],
                subdomain=gened_subdomain)
            company.save()
            user.save()
            company.users.add(user)
            user.owned_company.add(company)
            mail_context = {
                'site_name': settings.SITE_NAME,
                'gu__user__email': user.email,
            }
            UserRegistrationEmail(**mail_context).send(
                to=(user.email,),
                bcc=settings.BCC_EMAILS)
        return user


class PasswordResetForm(forms.Form):

    email = forms.EmailField(label=_("Email"), max_length=254)
    error_messages = (_("User with such email is not registered."))

    def clean_email(self):
        email = self.cleaned_data['email']
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
