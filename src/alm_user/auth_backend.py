from models import Account
from django.core.exceptions import PermissionDenied


class MyAuthBackend(object):

    def authenticate(self, username=None, password=None):
        try:
            acc = Account.objects.get(**{Account.USERNAME_FIELD: username})
            if acc.check_password(password):
                return acc
            raise PermissionDenied
        except Account.DoesNotExist:
            return None

    def get_user(self, acc_id):
        """ Get a User object from the acc_id. """
        try:
            return Account.objects.select_related('company', 'user').get(id=acc_id)
        except Account.DoesNotExist:
            return None
