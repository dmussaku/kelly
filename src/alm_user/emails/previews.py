import random
import hashlib

from almanet.mailviews_mixins import PreviewForm
from django.utils.translation import ugettext_lazy as _
from django import forms
from mailviews.previews import site, Preview
from .messages import UserResetPasswordEmail


def gen_activation_key():
    return hashlib.sha1(str(random.random())).hexdigest()[:20]


class UserResetPasswordEmailForm(PreviewForm):
    token = forms.CharField(label=_("token"), initial=gen_activation_key())
    site_name = forms.CharField(label=_('Site name'), initial='Alma.net')
    protocol = forms.CharField(label=_('Http protocol'), initial='https')


class UserResetPasswordEmailPreview(Preview):
    message_view = UserResetPasswordEmail
    form_class = UserResetPasswordEmailForm


site.register(UserResetPasswordEmailPreview)
