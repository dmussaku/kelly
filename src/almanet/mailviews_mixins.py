from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model


class PreviewForm(forms.Form):
    gu__user__email = forms.EmailField(
        initial='r.kamun@gmail.com',
        label='User')

    def get_message_view_kwargs(self):
        return self.cleaned_data


class ContextMixin(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx.update(kwargs)
        ctx.update(self.kwargs)
        return super(ContextMixin, self).get_context_data(**ctx)


class DomainMixin(object):

    def get_context_data(self, **kwargs):
        return super(DomainMixin, self).get_context_data(
            domain=settings.SITE_DOMAIN, **kwargs)


class UserMixin(object):

    def get_context_data(self, **kwargs):
        result = {}
        for key, value in kwargs.iteritems():
            if key.startswith('gu__'):
                _, dest, search_field = key.split('__')
                User = get_user_model()
                result[dest] = User.objects.filter(
                    **{search_field: value}).first()
        kwargs.update(result)
        return super(UserMixin, self).get_context_data(**kwargs)


class SendAdminsMixin(object):

    def send(self, *args, **kwargs):
        to = kwargs.pop('to', None) or [
            admin[1] for admin in settings.MANAGERS]
        super(SendAdminsMixin, self).send(to=to, *args, **kwargs)
