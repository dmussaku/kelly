from django import forms
from alm_user.models import User
from django.contrib import auth

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
