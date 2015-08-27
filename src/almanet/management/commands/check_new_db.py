#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from alm_crm.models import *
from almanet.models import *
from alm_company.models import *
from alm_user.models import *
from django.db import models

def check_subscr_object_count(f, subscr_models):
    object_count = sum([m.objects.count() for m in subscr_models])
    f.write('Number of SubscriptioObject objects %s \n' % object_count)
    f.write('----------------------------------------\n')

def check_object_count_by_subscr_id(f, subscr_models):
    for company in Company.objects.all():
        object_count = sum([m.objects.filter(company_id=company.id).count() for m in subscr_models])
        f.write('   Object count for company {%s} = {%s}\n' % (company, object_count))
        f.write('----------------------------------------\n')

def check_users_count(f):
    f.write('User count = %s\n' % User.objects.count())
    f.write('Company count = %s\n' % Company.objects.count())
    f.write('---------------------------------------------\n')

'''
Contact, SalesCycle, Activity, Comment
'''

def check_object_count_by_owner(f, subscr_models):
    for user in User.objects.all():
        object_count = sum([
            Contact.objects.filter(owner_id=user.id).count(),
            SalesCycle.objects.filter(owner_id=user.id).count(),
            Activity.objects.filter(owner_id=user.id).count(),
            Comment.objects.filter(owner_id=user.id).count(),    
            ])  
        f.write('       Object count for %s is %s\n' % (user, object_count))


class Command(BaseCommand):
    help = 'Check database for existense main fields of objects, as is contact has \
     default cycle, is cycle has contact, is activity on cycle, is contact has owner \
     is product has sales_cycles'

    def handle(self, *args, **options):
        subscr_models = [m for m in models.get_models() 
            if issubclass(m, SubscriptionObject) and not m._meta.abstract]
        f = open('new_db_integrity','w')
        check_subscr_object_count(f, subscr_models)
        check_users_count(f)
        check_object_count_by_subscr_id(f, subscr_models)
        check_object_count_by_owner(f, subscr_models)
        f.close()
