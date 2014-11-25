from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.conf import settings
from os import path as os_path


main_database = 'default'
db_backup_filename = os_path.join(
    os_path.expanduser('~/.almanet/test_data__db_backup.json'))


def path_rel(*x):
    return os_path.join(settings.BASE_DIR, *x)


def load_fixtures():
    fixtures = (
        'users', 'companies', 'services', 'subscriptions', 'crmusers',
        'vcards', 'contacts', 'sales_cycles', 'products', 'values',
        'activities', 'comments',
        'mentions')

    # syncdb, migrate on main_database db and delete all data
    management.call_command('syncdb', database=main_database)
    management.call_command('migrate', database=main_database)
    management.call_command('flush', database=main_database, interactive=False,
                            verbosity=0)

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
                                exclude=['contenttypes'])
    load_fixtures()


def trash():
    # clear
    management.call_command('flush', database=main_database, interactive=False,
                            verbosity=0)
    # load from backup fixture file
    management.call_command('loaddata', db_backup_filename,
                            database=main_database)


class Command(BaseCommand):
    args = '<action>'  # action = deploy OR trash
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
                deploy()
            elif command == 'trash':
                trash()

            self.stdout.write('test_data %sed' % command)
