from django.views.generic import ListView
from django.views.generic.base import TemplateView, TemplateResponse
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache

from alm_user.models import User
from alm_company.models import Company
from alm_user.forms import RegistrationForm, UserBaseSettingsForm, UserPasswordSettingsForm

class UserListView(ListView):

    def get_context_data(self, **kwargs):
        return super(UserListView, self).get_context_data(**kwargs)


class UserRegistrationView(CreateView):

    form_class = RegistrationForm
    success_url = reverse_lazy('user_profile_url')
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
        post_reset_redirect = reverse_lazy('user_login')

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


class UserProfileView(TemplateView):
    """
    Shows users profile info
    """

    def get_context_data(self, **kwargs):
        ctx = super(UserProfileView, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        try:
            ctx['company'] = Company.objects.get(owner=self.request.user)
        except:
            pass
        return ctx

class UserProfileSettings(UpdateView):
    """
    Profile settings base view
    """

    model = User
    form_class = UserBaseSettingsForm
    success_url = reverse_lazy('user_profile_url')

    def get_object(self, **kwargs):
        return self.request.user
