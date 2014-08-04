from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from alm_user.models import User
from alm_user.emails import UserResetPasswordEmail

# need to finish validation errors for the passwords form


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(),
                               max_length=100)
    confirm_password = forms.CharField(widget=forms.PasswordInput(),
                                       max_length=100)

    class Meta:

        model = User
        fields = ['first_name', 'last_name', 'email']

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
            user.save()
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



            # subject = loader.render_to_string(subject_template_name, c)
            # # Email subject *must not* contain newlines
            # subject = ''.join(subject.splitlines())
            # email = loader.render_to_string(email_template_name, c)
            # send_mail(subject, email, from_email, [user.email])
