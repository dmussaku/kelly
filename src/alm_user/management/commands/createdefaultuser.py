import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import User, UserManager, Account
from alm_company.models import Company
from almanet.models import Service, Subscription
from alm_crm.models import CRMUser

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
            acc = Account.objects.get(email=email, company=c)
            u = acc.user
            sys.stderr.write("Error: bwayne@batman.bat email is already taken.\n")
        except (Account.DoesNotExist, KeyError):
            u = UserManager.create_user(first_name=first_name, last_name=last_name)
            acc = Account.objects.create_user(
                email=email, password=password, user=u, company=c, is_admin=True)
            sys.stderr.write("Account and User created successfully.\n")        
        subscription.user = u
        subscription.organization = c
        subscription.is_active = True
        subscription.save()
