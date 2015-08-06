from models import Account
from alm_company.models import Company
from almanet.middleware import AlmanetSessionMiddleware
from django.core.exceptions import PermissionDenied
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.middleware.csrf import rotate_token

def login(request, account):

    request.session = AlmanetSessionMiddleware.create_session(request, account)

    request.account = account
    rotate_token(request)
    user_logged_in.send(sender=account.__class__, request=request, user=account)


def logout(request):
    account = getattr(request, 'account', None)
    if hasattr(account, 'is_authenticated') and not account.is_authenticated():
        account = None
    user_logged_out.send(sender=account.__class__, request=request, user=account)

    request.session.flush()

    if hasattr(request, 'account'):
        from alm_user.models import AnonymousAccount
        request.account = AnonymousAccount()


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