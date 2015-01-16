import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import User, UserManager

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--first_name', dest='first_name', default=None,
            help='Enter first_name for the user.'),
        make_option('--last_name', dest='last_name', default=None,
            help='Enter last_name address for the user.'),
        make_option('--email', dest='email', default=None,
            help='Enter email address for the user.'),
        make_option('--password', dest='password', default=None,
            help='Enter password for the user.'),
    )
    help = 'Create user specifying his options.'

    def handle(self, *args, **options):
        first_name = options.get('first_name', None)
        last_name = options.get('last_name', None)
        email = options.get('email', None)
        password = options.get('password', None)

        try:
            User.objects.get(email=email)
        except (User.DoesNotExist, KeyError):
            UserManager().create_user(first_name, last_name, email, password)
        else:
            sys.stderr.write("Error: That email is already taken.\n")
