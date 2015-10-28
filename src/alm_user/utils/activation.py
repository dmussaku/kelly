# -*- coding: utf-8 -*-
"""
A two-step (registration followed by activation) workflow, implemented
by emailing an HMAC-verified timestamped activation token to the user
on signup.

"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.template.loader import render_to_string


REGISTRATION_SALT = settings.REGISTRATION_SALT
SITE_URL = settings.SITE_NAME


class RegistrationHelper(object):
    """docstring for RegistrationHelper"""
    email_body_template = 'emails/activation_link_email.txt'
    email_subject_template = 'emails/activation_link_subject.txt'

    @classmethod
    def get_activation_key(cls, account):
        """
        Generate the activation key which will be emailed to the user.

        """
        User = get_user_model()

        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        key_struct = {
            "username": getattr(account.user, User.USERNAME_FIELD),
            "subdomain": account.company.subdomain
        }
        protected_key_struct = signing.dumps(key_struct)

        activation_key = signer.sign(protected_key_struct)
        return activation_key

    @classmethod
    def get_email_context(cls, activation_key):
        """
        Build the template context used for the activation email.

        """

        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': SITE_URL,
        }

    @classmethod
    def send_activation_email(cls, account):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.

        """
        activation_key = cls.get_activation_key(account)
        context = cls.get_email_context(activation_key)
        subject = render_to_string(cls.email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.

        subject = ''.join(subject.splitlines())
        message = render_to_string(cls.email_body_template,
                                   context)
        account.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
