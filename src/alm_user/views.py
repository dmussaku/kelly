from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.contrib import auth
from authbackend import MyAuthBackend
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from alm_user.models import User
from alm_user.forms import RegistrationForm, UserBaseSettingsForm, UserPasswordSettingsForm

class UserListView(ListView):

    def get_context_data(self, **kwargs):
        return super(UserListView, self).get_context_data(**kwargs)


class UserRegistrationView(CreateView):

    form_class = RegistrationForm
    success_url = reverse_lazy('user_list')
    template_name = 'user/user_registration.html'


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        m = MyAuthBackend()
        user = m.authenticate(email, password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse_lazy('user_list'))
        else:
            return render(request, 'user/user_login.html',
                          {'message': 'Email or password incorrect'})
    return render(request, 'user/user_login.html')


def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse_lazy('user_list'))


def password_reset(request):
    #template_name='user/password_reset.html'
    if request.method == 'POST':
        email = request.POST.get('email', '')
        if email:
            try:
                u = User.objects.get(email=email)
                #make a user reset the password
                u.first_name
                return HttpResponse('Email with password change has been sent')
            except:
                return render(request, 'user/password_reset.html',
                              {'message': 'No user With that particular email'
                               })
        else:
            return render(request, 'user/password_reset.html',
                          {'message': 'Email wasnt entered'})
    return render(request, 'user/password_reset.html')

class UserProfileView(TemplateView):
    """
    Shows users profile info
    """

    def get_context_data(self, **kwargs):
        ctx = super(UserProfileView, self).get_context_data(**kwargs)
        # should be:
        # kwargs['user'] = self.request.user
        ctx['user'] = User.objects.get(id=1)
        return ctx

class UserProfileSettings(UpdateView):
    """
    Profile settings base view
    """

    model = User
    form_class = UserBaseSettingsForm
    success_url = reverse_lazy('user_profile_url')

    def get_object(self, **kwargs):
        return User.objects.get(id=1)
