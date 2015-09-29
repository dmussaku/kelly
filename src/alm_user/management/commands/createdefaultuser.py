import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import User, Account
from alm_company.models import Company
from almanet.models import Service, Subscription


class Command(BaseCommand):
    help = 'Create user with email b.wayne@batman.bat and password 123, also creates \
    associated company with subdomain bwayne. Also creates a Service object called AlmCRM \
    and a subscription object thus connecting bwayne to almacrm service'
    # option_list = BaseCommand.option_list + (
    #     make_option('--is_admin', dest='is_admin', default=False,
    #                 help='Enter is the user admin of the company, False by default')
    # )

    def handle(self, *args, **options):
        is_admin = options.get('is_admin', False)
        is_supervisor = True
        first_name = 'Bruce'
        last_name = 'Wayne'
        email = 'b.wayne@batman.bat'
        password = '123'

        subdomain = 'almacloud'
        name = 'AlmaCloud'
        try:
            service = Service.objects.get(slug='crm')
        except:
            service = Service()
            service.title = u'CRM'
            service.save()
        subscription = Subscription()
        subscription.service = service
        try:
            c=Company.objects.get(subdomain=subdomain)
        except (Company.DoesNotExist, KeyError):
            c = Company.build_company(name=name, subdomain=subdomain)
            sys.stderr.write("Company created successfully.\n")

        try:
            u = User.objects.get(email=email)
            acc = Account.objects.get(user=u, company=c)
            sys.stderr.write("Error: bwayne@batman.bat email is already taken.\n")
        except User.DoesNotExist:
            u = User.objects.create_user(email=email, password=password,
                    first_name=first_name, last_name=last_name, is_admin=True)
        except Account.DoesNotExist:
            acc = Account.objects.create_account(user=u, company=c, is_supervisor=is_supervisor)
        finally:
            sys.stderr.write("Account and User created successfully.\n")
        subscription.user = u
        subscription.organization = c
        subscription.is_active = True
        subscription.save()
