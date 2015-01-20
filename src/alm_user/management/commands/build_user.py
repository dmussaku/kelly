import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import User, UserManager
from alm_company.models import Company

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
        make_option('--company_name', dest='company_name', default=None,
                    help='Enter company name for the user, the company exists, \
                    user will set to the company, else will create new \
                    company where the user is admin'),
        make_option('--is_active', dest='is_active', default=True,
                    help='Enter is the user active now, default True.'),
        make_option('--is_admin', dest='is_admin', default=False,
                    help='Enter is the user admin of the company')
    )
    help = 'Create user specifying his options. If you want to specify company, enter company name.'

    def handle(self, *args, **options):
        first_name = options.get('first_name', None)
        last_name = options.get('last_name', None)
        email = options.get('email', None)
        password = options.get('password', None)
        company_name = options.get('company_name', None)
        is_active = options.get('is_active', True)
        is_admin = options.get('is_admin', False)

        try:
            User.objects.get(email=email)
        except (User.DoesNotExist, KeyError):
            user = UserManager().create_user(first_name, last_name, email, password)

            if company_name:
                try:
                    company = Company.objects.get(name=company_name)
                except Company.DoesNotExist:
                    company = Company.build_company(name=company_name, owner=user)
                    is_admin = True
                user.company.add(company)

            user.is_active = is_active
            user.is_admin = is_admin
            user.save()
        else:
            sys.stderr.write("Error: That email is already taken.\n")
