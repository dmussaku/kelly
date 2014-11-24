from django.core.management.base import BaseCommand, CommandError
import subprocess


class Command(BaseCommand):
    help = '''generate epydoc files to almanet/almanet/api_docs/
    epydoc -v --html src/alm_crm/api.py -o api_docs --parse-only'''

    def handle(self, *args, **options):
        subprocess.call(['epydoc', '-v',
                        '--html', 'src/alm_crm/api.py',
                        '-o', 'api_docs',
                        '--parse-only'])
