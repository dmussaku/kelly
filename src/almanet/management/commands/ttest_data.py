from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.conf import settings
from os import path as os_path
from optparse import make_option
from almanet.models import Subscription, Service
from alm_company.models import Company
from alm_user.models import User
from alm_vcard.models import VCard
from alm_crm.models import \
(
    CRMUser,
    Contact
)


main_database = 'default'
db_backup_filename = os_path.join(
    os_path.expanduser('~/.almanet/test_data__db_backup.json'))
few_db_backup_filename = os_path.join(
    os_path.expanduser('~/.almanet/test_data__db_few_backup.json'))


def path_rel(*x):
    return os_path.join(settings.BASE_DIR, *x)


def load_fixtures():
    fixtures = (
        'services', 'vcard', 'user', 'company', 'subscription', 'products',
        'crmuser', 'contact', 'sales_cycles', 'activities', 'comments',
        'mentions', 'sc_prod_stat')

    # syncdb, migrate on main_database db and delete all data
    #management.call_command('syncdb', database=main_database)
    #management.call_command('migrate', database=main_database)
    #management.call_command('flush', database=main_database, interactive=False, verbosity=0)

    # load fixtures
    for fixture_name in fixtures:
        management.call_command(
            'loaddata',
            path_rel('alm_crm/fixtures/test_data/%s.json' % fixture_name),
            database=main_database)


def deploy():
    # make a backup
    with open(db_backup_filename, 'w') as f:
        management.call_command('dumpdata', database=main_database, stdout=f,
                                exclude=['contenttypes', 'corsheaders'])
    trash()
    load_fixtures()


def trash():
    # clear
    management.call_command('flush', database=main_database, interactive=False,
                            verbosity=0)
    # load from backup fixture file
    management.call_command('loaddata', db_backup_filename,
                            database=main_database)
    Subscription.objects.all().delete()
    Service.objects.all().delete()
    Company.objects.all().delete()
    User.objects.all().delete()
    CRMUser.objects.all().delete()
    VCard.objects.all().delete()

def load_fixtures_few():
    fixtures = (
        'services', 'vcard_few', 'user_few', 'company_few', 'subscription_few', 'products_few',
        'crmuser_few', 'contact_few', 'sales_cycles_few', 'activities_few', 'comments_few',
        'mentions', 'sc_prod_stat_few')

    # syncdb, migrate on main_database db and delete all data
    #management.call_command('syncdb', database=main_database)
    #management.call_command('migrate', database=main_database)
    #management.call_command('flush', database=main_database, interactive=False, verbosity=0)

    # load fixtures
    for fixture_name in fixtures:
        management.call_command(
            'loaddata',
            path_rel('alm_crm/fixtures/test_data/%s.json' % fixture_name),
            database=main_database)


def deploy_few():
    # make a backup
    with open(few_db_backup_filename, 'w') as f:
        management.call_command('dumpdata', database=main_database, stdout=f,
                                exclude=['contenttypes', 'corsheaders'])
    trash()
    load_fixtures_few()

class Command(BaseCommand):
    args = '<action>'  # action = deploy OR trash
    option_list = BaseCommand.option_list + (
        make_option('--few', action='store_true', dest='few', default=False, 
            help='for deploying '),
    )
    help = 'deploy - roll testing fixtures, trash - unrole testing fixtures'

    def handle(self, *args, **options):
        try:
            command = args[0]
            if not command in ('deploy', 'trash'):
                raise
        except:
            raise CommandError(
                'test_data [deploy, trash] - action does not provided')
        if command == 'deploy':
            if options['few']:
                deploy_few()
            else:
                deploy()
        elif command == 'trash':
            trash()

        self.stdout.write('test_data %sed' % command)
