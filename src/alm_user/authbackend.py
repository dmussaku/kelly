from models import User
from django.contrib.auth import models


class MyAuthBackend(object):

    def authenticate(self, username=None, password=None):
        try:
            u = User.objects.get(**{User.USERNAME_FIELD: username})
            if u.check_password(password):
                return u
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
