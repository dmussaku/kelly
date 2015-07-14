import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_company.models import Company
from almanet.settings import DEFAULT_SERVICE
from almanet.models import Service, Subscription
from alm_crm.models import Contact, SalesCycle, Activity, CRMUser, Product, ContactList
from alm_vcard.models import VCard
import logging

def check_for_global_cycle_existence():
    print ("******** Check is Contact has global cycle ********")
    for contact in Contact.objects.all():
        try:
            sales_cycles = contact.sales_cycles.filter(is_global=True).count()
            if sales_cycles > 1:
                logging.warning("Contact with ID: %s has %s global sales cycles"%(contact.id, sales_cycles))
            elif not sales_cycles:
                logging.warning("Contact with ID: %s doesn't have global cycle"%(contact.id))
        except SalesCycle.DoesNotExist:
            logging.warning("Contact with ID: %s doesn't have global cycle"%(contact.id))
    print "******** Checking finished ******** \n"

def check_is_cycle_has_contact():
    print "******** Check is SalesCycle has Contact ********"
    for sales_cycle in SalesCycle.objects.all():
        try:
            contact = sales_cycle.contact
            if not contact:
                logging.warning("SalesCycle with ID: %s doesn't have contact"%(sales_cycle.id))
            if contact.subscription_id != sales_cycle.subscription_id:
                logging.warning("SalesCycle with ID: %s and contact with ID: %s have different subscription_ids: %s and %s"%(sales_cycle.id, contact.id, sales_cycle.subscription_id, contact.subscription_id))
        except Contact.DoesNotExist:
            logging.warning("SalesCycle with ID: %s doesn't have contact"%(sales_cycle.id))
    print "******** Checking finished ******** \n"

def check_is_activity_on_cycle():
    print "******** Check is Activity has SalesCycle ********"
    for activity in Activity.objects.all():
        try:
            sales_cycle = activity.sales_cycle
            if not sales_cycle:
                logging.warning("Activity with ID: %s doesn't have sales_cycle"%(activity.id))
            if activity.subscription_id != sales_cycle.subscription_id:
                logging.warning("Activity with ID: %s and SalesCycle with ID: %s have different subscription_ids: %s and %s"%(activity.id, sales_cycle.id, activity.subscription_id, sales_cycle.subscription_id))
        except SalesCycle.DoesNotExist:
            logging.warning("Activity with ID: %s doesn't have sales_cycle"%(activity.id))
    print "******** Checking finished ******** \n"
    
def check_is_contact_has_owner():
    print "******** Check is Contact has Owner ********"
    for contact in Contact.objects.all():
        try:
            owner = contact.owner
            if not owner:
                logging.warning("Contact with ID: %s doesn't have owner"%(contact.id))
            if contact.subscription_id != owner.subscription_id:
                logging.warning("Contact with ID: %s and his owner with ID: %s have different subscription_ids: %s and %s"%(contact.id, owner.id, contact.subscription_id, owner.subscription_id))
        except CRMUser.DoesNotExist:
            logging.warning("Contact with ID: %s doesn't have owner"%(contact.id))
    print "******** Checking finished ******** \n"

def check_is_product_has_sales_cycles():
    print "******** Check is Product has SalesCycles ********"
    for product in Product.objects.all():
        try:
            sales_cycles = product.sales_cycles
            if not sales_cycles:
                logging.warning("Product with ID: %s doesn't have sales_cycles"%(product.id))
            else:
                for sales_cycle in sales_cycles.all():
                    if product.subscription_id != sales_cycle.subscription_id:
                        logging.warning("Product with ID: %s and sales_cycle with ID: %s have different subscription_ids: %s and %s"%(product.id, sales_cycle.id, product.subscription_id, sales_cycle.subscription_id))

        except SalesCycle.DoesNotExist:
            logging.warning("Product with ID: %s doesn't have sales_cycles"%(product.id))
    print "******** Checking finished ******** \n"

def check_is_contact_has_vcard():
    print "******** Check is Contact has VCard ********"
    for contact in Contact.objects.all():
        try:
            vcard = contact.vcard
            if not vcard:
                logging.warning("Contact with ID: %s doesn't have vcard"%(contact.id))
        except VCard.DoesNotExist:
            logging.warning("Contact with ID: %s doesn't have vcard"%(contact.id))
    print "******** Checking finished ******** \n"

def check_are_contact_in_contactlist_exist():
    print "******** Check are Contacts in ContactList exist  ********"
    for contact_list in ContactList.objects.all():
        try:
            contacts = contact_list.contacts
            for contact in contacts.all():
                if not contact.pk:
                    logging.warning("ContactList with ID: %s has nonexistent contact %s"%(contact_list.id, contact))
        except VCard.DoesNotExist:
            logging.warning("Contact with ID: %s doesn't have vcard"%(contact.id))
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
        check_are_contact_in_contactlist_exist()

        self.stdout.write('DATABASE CHECKING HAS BEEN FINISHED')
