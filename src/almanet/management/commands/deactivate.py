import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_company.models import Company
from almanet.settings import DEFAULT_SERVICE
from almanet.models import Service, Subscription

class Command(BaseCommand):
    args = '<company_name>'
    # option_list = BaseCommand.option_list + (
    #     make_option('--company_name', dest='company_name', default=None,
    #         help='Enter name of the organization.'),
    # )
    help = 'Enter a company name for activate a subscription'

    def handle(self, *args, **options):
        try:
            company = Company.objects.get(name=args[0])
        except Company.DoesNotExist:
            sys.stderr.write('Company with that name does not exist, please, enter right name\n')
        else:
            subscriptions = company.subscriptions.filter(is_active=True)
            if not subscriptions:
                print 'There not any active subscriptions'
                return

            for subscription in subscriptions:
                print 'ID: %s, User: %s'%(subscription.pk, subscription.user.get_full_name())

            subscription = raw_input('Enter subscription id:')
            try: 
                subscription = Subscription.objects.get(id=subscription)
            except (Subscription.DoesNotExist, ValueError):
                sys.stderr.write('Please, enter valid data\n')
                return
            subscription.is_active = False
            subscription.save()

            print 'DEACTIVATED: ID: %s, User: %s\n'%(subscription.pk, subscription.user.get_full_name())
