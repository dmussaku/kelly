import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import User, UserManager
from alm_company.models import Company

class Command(BaseCommand):
    help = 'Create user with email b.wayne@batman.bat and password 123, also creates associated company with subdomain bwayne'

    def handle(self, *args, **options):
        first_name = 'Bruce'
        last_name = 'Wayne'
        email = 'b.wayne@batman.bat'
        password = '123'

        subdomain = 'bwayne'
        name = 'Wayne Enterprise'

        try:
            User.objects.get(email=email,)
        except (User.DoesNotExist, KeyError):
            try:
                Company.objects.get(subdomain=subdomain)
            except (Company.DoesNotExist, KeyError):
                u = UserManager().create_user(first_name, last_name, email, password)
                c = Company(name=name, subdomain=subdomain)
                c.save()
                c.users.add(u)
                u.owned_company.add(c)
                sys.stderr.write("User and company created successfully.\n")
            else:
                sys.stderr.write("Error: bwayne subdomain is already taken. Did not created anything.\n")
        else:
            sys.stderr.write("Error: bwayne@batman.bat email is already taken.\n")
