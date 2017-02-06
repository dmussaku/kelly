from django.core.management.base import BaseCommand
from almanet.preparations import pre

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        pre()
