import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import User, UserManager
from alm_company.models import Company
from almanet.settings import DEFAULT_SERVICE
from almanet.models import Service, Subscription

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--service', dest='service', default=DEFAULT_SERVICE,
            help='Enter service name, default CRM'),
        make_option('--user_email', dest='user_email', default=None,
            help='Enter last_name address for the user.'),
        make_option('--is_active', dest='is_active', default=True,
            help='Enter is the subscription active, default True'),
    )
    help = 'Create Subscription specifying his options.'

    def handle(self, *args, **options):
        service_slug = options.get('service', DEFAULT_SERVICE).lower()
        user_email = options.get('user_email', None)
        is_active = options.get('is_active', True)

        try:
            user = User.objects.get(email=user_email)
        except (User.DoesNotExist, KeyError):
            sys.stderr.write("Error: The user you entered does not exist, please enter exist one or create user using command build_account.\n")
        else:
            service = Service.objects.get(slug=service_slug)
            user.connect_service(service)
