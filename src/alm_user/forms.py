from django import forms
from django.forms import ModelForm
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _

from alm_user.models import User

#need to finish validation errors for the passwords form


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


class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    errors = ["Enter Password", "The password you've entered is incorrect",
              "A user with given email doesn't exist"]

    def clean(self):
        email = self.cleaned_data.get('email', None)
        password = self.cleaned_data.get('password', None)
        if (email):
            try:
                u = User.objects.get(email=email)
                if (not password):
                    raise forms.ValidationError(errors[0])
                else:
                    if (password != u.password):
                        raise forms.ValidationError(errors[1])
            except:
                raise forms.ValidationError(errors[2])
        return super(LoginForm, self).clean()

class UserBaseSettingsForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'city', 'country']

class UserPasswordSettingsForm(forms.Form):

    old_password = forms.CharField(widget=forms.PasswordInput, label=_("Old password"))
    password = forms.CharField(widget=forms.PasswordInput(), label=_('New Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(), label=_('Repeat your password'))

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
            raise forms.ValidationError(self.error_messages['old_password_incorrect'])
        return old_password

    def clean(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password and password2:
            if password != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'])
        return self.cleaned_data

    def save(self, *args, **kwargs):
        self.user.set_password(self.cleaned_data['password'])
        self.user.save()
        return self.user