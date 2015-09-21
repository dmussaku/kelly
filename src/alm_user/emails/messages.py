from almanet.mailviews_mixins import ContextMixin, UserMixin, DomainMixin
from mailviews.messages import TemplatedEmailMessageView


class UserResetPasswordEmail(
        ContextMixin, UserMixin, DomainMixin, TemplatedEmailMessageView):
    r"""Sends an activation email to the `user_email`.
    The activation email uses two templates:

        ``emails/activation_email_subject.txt``
          subject of the email

        ``emails/activation_email.txt``
          body of the email

        Context variables

        ``user``
          newly created user instance
        ``activation_key``
          an activation key for the new account
        ``expiration_days``
          number of days remaining during which the account can be activated
    """

    subject_template_name = 'emails/password_reset_subject.txt'
    body_template_name = 'emails/password_reset_email.txt'


class UserRegistrationEmail(
        ContextMixin, UserMixin, DomainMixin, TemplatedEmailMessageView):
    r"""Sends a greeting email after registration to the `user_email`.
    The activation email uses two templates:

        ``emails/registration_greeting_subject.txt``
          subject of the email

        ``emails/registration_greeting_email.txt``
          body of the email
    """

    subject_template_name = 'emails/registration_greeting_subject.txt'
    body_template_name = 'emails/registration_greeting_email.txt'


class SubdomainForgotEmail(
    ContextMixin, UserMixin, DomainMixin, TemplatedEmailMessageView):
    
    subject_template_name = 'emails/subdomain_forgot_subject.txt'
    body_template_name = 'emails/subdomain_forgot_email.txt'

