from django.forms import ModelForm
from django.contrib.auth.hashers import check_password
from django import forms
from django.utils.translation import ugettext_lazy as _

from user.models import User

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