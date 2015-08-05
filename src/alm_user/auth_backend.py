from models import Account
from alm_company.models import Company
from almanet.middleware import AlmanetSessionMiddleware
from django.core.exceptions import PermissionDenied
from django.contrib.auth.signals import user_logged_in
from django.middleware.csrf import rotate_token

def login(request, account):

    request.session = AlmanetSessionMiddleware.create_session(request, account)

    request.account = account
    rotate_token(request)
    user_logged_in.send(sender=account.__class__, request=request, user=account)


def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)

    # remember language choice saved to session
    language = request.session.get('django_language')

    request.session.flush()

    if language is not None:
        request.session['django_language'] = language

    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()


class MyAuthBackend(object):

    def authenticate(self, subdomain=None, username=None, password=None):
        try:
            try:
                company = Company.objects.get(subdomain=subdomain)
            except Company.DoesNotExist:
                return -1 # to say that there is no company with provided subdomain
            acc = Account.objects.get(**{Account.USERNAME_FIELD: username, 'company_id': company.id})
            if acc.check_password(password):
                return acc
            raise PermissionDenied
        except Account.DoesNotExist:
            return None

    def get_account(self, acc_id):
        """ Get a User object from the acc_id. """
        try:
            return Account.objects.select_related('company', 'user').get(id=acc_id)
        except Account.DoesNotExist:
            return None