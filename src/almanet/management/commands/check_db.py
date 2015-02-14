import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_company.models import Company
from almanet.settings import DEFAULT_SERVICE
from almanet.models import Service, Subscription
from alm_crm.models import Contact, SalesCycle, Activity, CRMUser, Product
from alm_vcard.models import VCard

def check_for_global_cycle_existence():
    print "******** Check is Contact has global cycle ********"
    for contact in Contact.objects.all():
        try:
            sales_cycles = contact.sales_cycles.filter(is_global=True).count()
            if sales_cycles > 1:
                print "WARNING: Contact with ID: %s has %s global sales cycles"%(contact.id, sales_cycles)
            elif sales_cycles < 1:
                print "WARNING: Contact with ID: %s doesn't have global cycle"%(contact.id)
        except SalesCycle.DoesNotExist:
            print "WARNING: Contact with ID: %s doesn't have global cycle"%(contact.id)
    print "******** Checking finished ******** \n"

def check_is_cycle_has_contact():
    print "******** Check is SalesCycle has Contact ********"
    for sales_cycle in SalesCycle.objects.all():
        try:
            contact = sales_cycle.contact
        except Contact.DoesNotExist:
            print "WARNING: SalesCycle with ID: %s doesn't have contact"%(sales_cycle.id)
    print "******** Checking finished ******** \n"

def check_is_activity_on_cycle():
    print "******** Check is Activity has SalesCycle ********"
    for activity in Activity.objects.all():
        try:
            activity = activity.sales_cycle
        except SalesCycle.DoesNotExist:
            print "WARNING: Activity with ID: %s doesn't have sales_cycle"%(activity.id)
    print "******** Checking finished ******** \n"
    
def check_is_contact_has_owner():
    print "******** Check is Contact has Owner ********"
    for contact in Contact.objects.all():
        try:
            owner = contact.owner
        except CRMUser.DoesNotExist:
            print "WARNING: Contact with ID: %s doesn't have owner"%(sales_cycle.id)
    print "******** Checking finished ******** \n"

def check_is_product_has_sales_cycles():
    print "******** Check is Product has SalesCycles ********"
    for product in Product.objects.all():
        try:
            sales_cycles = product.sales_cycles
        except SalesCycle.DoesNotExist:
            print "WARNING: Product with ID: %s doesn't have sales_cycles"%(product.id)
    print "******** Checking finished ******** \n"

def check_is_contact_has_vcard():
    print "******** Check is Contact has VCard ********"
    for contact in Contact.objects.all():
        try:
            vcard = contact.vcard
        except VCard.DoesNotExist:
            print "WARNING: Contact with ID: %s doesn't have vcard"%(vcard.id)
    print "******** Checking finished ******** \n"

class Command(BaseCommand):
    help = 'Check database for existense main fields of objects, as is contact has \
     default cycle, is cycle has contact, is activity on cycle, is contact has owner \
     is product has sales_cycles'

    def handle(self, *args, **options):
        check_for_global_cycle_existence()
        check_is_cycle_has_contact()
        check_is_activity_on_cycle()
        check_is_contact_has_owner()
        check_is_product_has_sales_cycles()
        check_is_contact_has_vcard()

        self.stdout.write('DATABASE CHECKING HAS BEEN FINISHED')
