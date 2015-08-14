import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.db.models import get_app, get_models
# from alm_company.models import Company
# from almanet.settings import DEFAULT_SERVICE
from almanet.models import Subscription, SubscriptionObject

class Command(BaseCommand):
    help = 'You should enter just command, after that you will be asked to enter subscription ids which you want to merge'

    def handle(self, *args, **options):
        subscription_to = raw_input('Please, enter subscription id to which you want to merge: ')
        subscription_from = raw_input('Please, enter subscription id which you want to merge(WARNING: this subscription will be deleted): ')

        alm_crm = get_app('alm_crm')
        for model in get_models(alm_crm):
            if hasattr(model(), 'subscription_id'):
                for instance in model.objects.filter(subscription_id=subscription_from):
                    instance.subscription_id = subscription_to
                    instance.save()

        Subscription.objects.get(id=subscription_from).delete()

        self.stdout.write('subscription %i has been merged with subscription %i and deleted'%(subscription_from, subscription_to))