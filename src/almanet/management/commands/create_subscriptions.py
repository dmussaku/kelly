#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from almanet.models import Plan, Subscription
from alm_company.models import Company

class Command(BaseCommand):

    def handle(self, *args, **options):
        for company in Company.objects.all():
            if not company.subscription:
                users = [account.user for account in company.accounts.all()] 
                if not users:
                    subscription = Subscription()
                else:
                    if [user for user in users if user.is_admin==True]:
                        user = users[0]
                    else:
                        user = users[0]
                        users[0].is_admin = True
                        user.save()
                    subscription = Subscription(
                        user=user,
                        )
                subscription.save()
                company.subscription = subscription
                company.save()
                print subscription


from django.db import transaction

def copy_contacts(old_user_id=None, old_company_id=None, new_user_id=None, new_company_id=None):
    with transaction.atomic():
        contacts = []
        activities = Activity.objects.filter(
            owner_id=old_user_id, company_id=old_company_id)
        for activity in activities:
            contacts.append(activity.sales_cycle.contact)
        '''
        copying contacts, going to be tough
        '''
        c_list = ContactList(
            title='Из Лабтроника', owner_id=new_user_id, company_id=new_company_id)
        c_list.save()
        for contact in contacts:
            vcard = vcard_deep_copy(contact)
            contact.pk = None
            contact.latest_activity = None
            contact.vcard = vcard
            contact.owner_id = new_user_id
            contact.company_id = new_company_id
            contact.mentions.clear()
            contact.comments.clear()
            contact.save()
            SalesCycle.create_globalcycle(
                    **{'company_id': contact.company_id,
                     'owner_id': contact.owner.id,
                     'contact_id': contact.id
                    }
                )
            c_list.contacts.add(contact)
        c_list.save()

def vcard_deep_copy(contact):
    vcard = contact.vcard
    original_id = vcard.pk
    print original_id
    vcard.pk = None
    vcard.save()
    new_id = vcard.pk
    print new_id
    for rel_obj in vcard._meta.get_all_related_objects():
        if rel_obj.name.startswith('alm_vcard'):
            print rel_obj.name
            model = rel_obj.model
            for obj in model.objects.filter(vcard_id=original_id):
                print 'saved'
                obj.pk = None
                obj.vcard_id = new_id
                obj.save()
    return vcard
    



