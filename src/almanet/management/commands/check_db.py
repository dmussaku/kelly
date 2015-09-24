import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from alm_company.models import Company
from almanet.settings import DEFAULT_SERVICE
from alm_user.models import Account, User
from almanet.models import Service, Subscription
from alm_crm.models import *
from alm_vcard.models import VCard, Tel, Email, Adr, Url
import logging
from django.db.models import get_app, get_models
import datetime

open('check_db.log', 'w').close()
logging.basicConfig(filename='check_db.log', level=logging.INFO)

def check_app_models_for_equality_company_id_with_owner():
    print "******** Check alm_crm models for equality of company_ids of object and object.owner ********"
    logging.info("MODEL_OWNER_COMPANY_IDS_CHECK")
    app = get_app('alm_crm')
    for model in get_models(app):
        if model.__name__ == "ActivityRecipient":
            continue
        for object in model.objects.all():
            if hasattr(object, 'owner'):
                if object.owner == None:
                    logging.warning('NO_OWNER {%s} ID {%s}'%(object.__class__.__name__, object.id))
                elif object.company_id != object.owner.accounts.first().company_id:
                    logging.warning('DIFFERENT_COMPANY_IDS {%s} ID {%s} {User} ID {%s}'%(object.__class__.__name__, object.id, object.owner.id))
            elif hasattr(object, 'company_id'):
                if object.company_id == None:
                    logging.warning('NO_COMPANY_ID {%s} ID {%s}'%(object.__class__.__name__, object.id))

    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"


def check_for_global_cycle_existence():
    print "******** Check is Contact has global cycle ********"
    logging.info("CONTACT GLOBAL CYCLE CHECK")
    for contact in Contact.objects.all():
        try:
            sales_cycles = contact.sales_cycles.filter(is_global=True)
            cycles_amount = sales_cycles.count()
            for sales_cycle in sales_cycles.all():
                if sales_cycle.owner != contact.owner:
                    logging.warning("DIFFERENT_OWNERS {SalesCycle} ID {%s} and {Contact} ID {%s}"%(sales_cycle.id, contact.id))
            if cycles_amount > 1:
                logging.warning("MORE_THAN_ONE_GLOBAL_CYCLE {Contact} ID {%s} AMOUNT %s"%(contact.id, cycles_amount))
            elif cycles_amount == 0:
                logging.warning("NO_ANY_GLOBAL CYCLES {Contact} ID {%s}"%(contact.id))
        except SalesCycle.DoesNotExist:
            logging.warning("NO_ANY_GLOBAL CYCLES {Contact} ID {%s}"%(contact.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_is_cycle_has_contact():
    print "******** Check is SalesCycle has Contact ********"
    logging.info("SALES CYCLE CONTACT CHECK")
    for sales_cycle in SalesCycle.objects.all():
        try:
            contact = sales_cycle.contact
            if not contact:
                logging.warning("NO_ANY_CONTACTS {SalesCycle} ID {%s}"%(sales_cycle.id))
            if contact.company_id != sales_cycle.company_id:
                logging.warning("DIFFERENT_COMPANY_IDS {SalesCycle} ID {%s} and {Contact} ID {%s}"%(sales_cycle.id, contact.id))
        except Contact.DoesNotExist:
            logging.warning("NO_ANY_CONTACTS {SalesCycle} ID {%s}"%(sales_cycle.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_is_activity_on_cycle():
    print "******** Check is Activity has SalesCycle ********"
    logging.info("ACTIVITY SALES CYCLE CHECK")
    for activity in Activity.objects.all():
        try:
            sales_cycle = activity.sales_cycle
            if not sales_cycle:
                logging.warning("NO_ANY_SALES_CYCLE {Activity} ID {%s}"%(activity.id))
            if activity.company_id != sales_cycle.company_id:
                logging.warning("DIFFERENT_COMPANY_IDS {Activity} ID {%s} and {SalesCycle} ID {%s}"%(activity.id, sales_cycle.id))
        except SalesCycle.DoesNotExist:
            logging.warning("NO_ANY_ACTIVITY {Activity} ID {%s}"%(activity.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"
    
def check_is_contact_has_owner():
    print "******** Check is Contact has Owner ********"
    logging.info("CONTACT OWNER CHECK")
    for contact in Contact.objects.all():
        try:
            owner = contact.owner
            if not owner:
                logging.warning("NO_ANY_OWNER {Contact} ID {%s}"%(contact.id))
            if contact.company_id != owner.accounts.first().company_id:
                logging.warning("DIFFERENT_COMPANY_IDS {Contact} ID {%s} and {User} ID {%s}"%(contact.id, owner.id))
        except CRMUser.DoesNotExist:
            logging.warning("NO_ANY_OWNER {Contact} ID {%s}"%(contact.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_is_product_has_sales_cycles():
    print "******** Check is Product has SalesCycles ********"
    logging.info("PRODUCT SALES_CYCLE CHECK")
    for product in Product.objects.all():
        try:
            sales_cycles = product.sales_cycles
            if not sales_cycles:
                logging.warning("NO_ANY_SALES_CYCLES {Product} ID {%s}"%(product.id))
            else:
                for sales_cycle in sales_cycles.all():
                    if product.company_id != sales_cycle.company_id:
                        logging.warning("DIFFERENT_COMPANY_IDS {Product} ID {%s} and {SalesCycle} ID {%s}"%(product.id, sales_cycle.id))

        except SalesCycle.DoesNotExist:
            logging.warning("NO_ANY_SALES_CYCLES {Product} ID {%s}"%(product.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_is_contact_has_vcard():
    print "******** Check is Contact has VCard ********"
    logging.info("CHECK CONTACT VCARD\n")
    for contact in Contact.objects.all():
        try:
            vcard = contact.vcard
            if not vcard:
                logging.warning("NO_ANY_VCARD {Contact} ID {%s}"%(contact.id))
        except VCard.DoesNotExist:
            logging.warning("NO_ANY_VCARD {Contact} ID {%s}"%(contact.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_are_contact_in_contactlist_exist():
    print "******** Check are Contacts in ContactList exist  ********"
    logging.info("CONTACT_LIST CONTACTS CHECK")
    for contact_list in ContactList.objects.all():
        try:
            contacts = contact_list.contacts
            for contact in contacts.all():
                if not contact.pk:
                    logging.warning("NON_EXISTENT_OBJECT {ContactList} ID {%s} OBJECT: %s"%(contact_list.id, contact))
                if contact_list.company_id != contact.company_id:
                    logging.warning("DIFFERENT_COMPANY_IDS {ContactList} ID {%s} and {Contact} ID {%s}"%(contact_list.id, contact.id))
        except VCard.DoesNotExist:
            logging.warning("NO_ANY_VCARD {Contact} ID {%s}"%(contact.id))
    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_is_share_has_contact():
    print "******** Check is Share has Contact and shared user ********"
    logging.info("SHARE CHECK")
    for share in Share.objects.all():

        contact = share.contact
        shared_from = share.share_from
        shared_to = share.share_to

        if contact == None:
            logging.warning("NO_ANY_CONTACT {Share} ID {%s}"%(share.id))

        if shared_from == None:
            logging.warning("NO_SHARED_FROM_USER {Share} ID {%s}"%(share.id))
        elif share.company_id != shared_from.accounts.first().company_id:
            logging.warning("DIFFERENT_COMPANY_IDS {Share} ID {%s} and {User} shared from ID {%s}"%(share.id, shared_from.id ))            

        if shared_to == None:
            logging.warning("NO_SHARED_TO_USER {Share} ID {%s}"%(share.id))
        elif share.company_id != shared_to.accounts.first().company_id:
            logging.warning("DIFFERENT_COMPANY_IDS {Share} ID {%s} and {User} shared to ID {%s}"%(share.id, shared_to.id))

        if share.company_id != contact.company_id:
            logging.warning("DIFFERENT_COMPANY_IDS {Share} ID {%s} and {Contact} ID {%s}"%(share.id, contact.id))

    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_subscription_milestones():
    print "******** Check is Subscription has a success and a fail Milestone ********"
    logging.info("SUBSCRIPTION SUCCESS AND FAIL MILESTONES CHECK")
    for subscription in Subscription.objects.all():
        success_milestones_amount = Milestone.objects.filter(company_id=subscription.id, is_system = 1).count()
        fail_milestones_amount = Milestone.objects.filter(company_id=subscription.id, is_system = 2).count()

        if success_milestones_amount != 1:
            logging.warning("ILLEGAL_AMOUNT_OF_MILESTONES {Subscription} ID {%s} TYPE {SUCCESS} AMOUNT {%i}"%(subscription.id, success_milestones_amount))

        if fail_milestones_amount != 1:
            logging.warning("ILLEGAL_AMOUNT_OF_MILESTONES {Subscription} ID {%s} TYPE {FAIL} AMOUNT {%i}"%(subscription.id, fail_milestones_amount))

    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"

def check_vcard_models_types():
    print "******** Check is alm_vcard app models for correct types ********"
    logging.info("VCARD MODELS TYPE CHECK")
    TEL_TYPE_CHOICES = Tel.TYPE_CHOICES
    EMAIL_TYPE_CHOICES = Email.TYPE_CHOICES
    ADR_TYPE_CHOICES = Adr.TYPE_CHOICES 
    URL_TYPE_CHOICES = Url.TYPE_CHOICES

    in_choices = False

    for tel in Tel.objects.all():
        in_choices = False
        for type_tuple in TEL_TYPE_CHOICES:
            if tel.type == type_tuple[0]:
                in_choices = True
        if not in_choices:
            logging.warning("ILLEGAL_TYPE {Tel} ID {%s} type {%s}"%(tel.id, tel.type))

    for email in Email.objects.all():
        in_choices = False
        for type_tuple in EMAIL_TYPE_CHOICES:
            if email.type == type_tuple[0]:
                in_choices = True
        if not in_choices:
            logging.warning("ILLEGAL_TYPE {Email} ID {%s} type {%s}"%(email.id, email.type))

    for adr in Adr.objects.all():
        in_choices = False
        for type_tuple in ADR_TYPE_CHOICES:
            if adr.type == type_tuple[0]:
                in_choices = True
        if not in_choices:
            logging.warning("ILLEGAL_TYPE {Adr} ID {%s} type {%s}"%(adr.id, adr.type))

    for url in Url.objects.all():
        in_choices = False
        for type_tuple in URL_TYPE_CHOICES:
            if url.type == type_tuple[0]:
                in_choices = True
        if not in_choices:
            logging.warning("ILLEGAL_TYPE {Url} ID {%s} type {%s}"%(url.id, url.type))


    logging.info("FINISHED\n")
    print "******** Checking finished ********\n"


class Command(BaseCommand):
    help = 'Check database for existense main fields of objects, as is contact has \
     default cycle, is cycle has contact, is activity on cycle, is contact has owner \
     is product has sales_cycles'

    def handle(self, *args, **options):
        self.stdout.write('DATABASE CHECKING STARTED')
        logging.info("%s CHECK DATABASE STARTED\n"%datetime.datetime.now())
        check_app_models_for_equality_company_id_with_owner()
        check_for_global_cycle_existence()
        check_is_cycle_has_contact()
        check_is_activity_on_cycle()
        check_is_contact_has_owner()
        check_is_product_has_sales_cycles()
        check_is_contact_has_vcard()
        check_are_contact_in_contactlist_exist()
        check_is_share_has_contact()
        check_subscription_milestones()
        check_vcard_models_types()
        logging.info("%s CHECK DATABASE FINISHED"%datetime.datetime.now())
        self.stdout.write('DATABASE CHECKING FINISHED')
