import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_user.models import PermissionConfiguration


class Command(BaseCommand):
    help = 'Creates PermissionConfiguration entities'
    # option_list = BaseCommand.option_list + (
    #     make_option('--is_admin', dest='is_admin', default=False,
    #                 help='Enter is the user admin of the company, False by default')
    # )

    def handle(self, *args, **options):

        for index, code in enumerate(PermissionConfiguration.CODES):
            pc = PermissionConfiguration(code=code, bitnumber=index,
                                         description=PermissionConfiguration.CODES_OPTIONS[index][1])
            pc.save()
            sys.stdout.write("%s. %s created successfully.\n" % (index, code.upper()))
