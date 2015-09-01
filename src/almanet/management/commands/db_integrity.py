#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from alm_crm.models import *
from almanet.models import *
from alm_company.models import *
from alm_user.models import *
from django.db import models
from django.db.models import get_app, get_models
import logging
from django.db import connections
from almanet.models import SubscriptionObject

open('db_integrity.log', 'w').close()
logging.basicConfig(filename='db_integrity.log', level=logging.INFO)

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'almanet',
        'TEST_NAME': 'test_mobiliuz',
        'USER':'postgres',
        'PASSWORD': 'postgres',
        'HOST':'localhost',
        'PORT':'5432'
    },
    'old': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'old_almanet',
        'TEST_NAME': 'test_mobiliuz',
        'USER':'postgres',
        'PASSWORD': 'postgres',
        'HOST':'localhost',
        'PORT':'5432'
    }
}

Sample Databases setting at .conf.py file, old is the old database taken from one of the snapshots
new one is the new architecture database with all the migrations applied.
'''

def count(raw_query):
    i = 0
    for r in raw_query:
        i += 1
    return i

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def check_object_count(model_list):
    sql_query = 'SELECT * FROM'
    for model_name in model_list:
        new_query = model_name.objects.raw(
            sql_query + ' {}'.format(model_name._meta.db_table))
        old_query = model_name.objects.raw(
            sql_query + ' {}'.format(model_name._meta.db_table)).using('old')
        if count(new_query) != count(old_query):
            logging.warning('Integrity fault at {}'.format(model_name))
    
def check_objects_by_subscription(model_list):
    sql_query = 'SELECT * FROM'
    subscriptions = Subscription.objects.using('old').all()
    for subscription in subscriptions:
        company_id = subscription.organization_id
        for model_name in model_list:
            new_query = model_name.objects.raw(
                sql_query + ' {}'.format(model_name._meta.db_table) + ' WHERE company_id={}'.format(company_id))
            old_query = model_name.objects.raw(
                sql_query + ' {}'.format(model_name._meta.db_table) + ' WHERE subscription_id={}'.format(subscription.id)).using('old')
            if count(new_query) != count(old_query):
                logging.warning('Integrity fault at {} at company {} subscription {}'.format(model_name, company_id, subscription.id))

def check_objects_by_owner(model_list):
    sql_query = 'SELECT * FROM alm_crm_crmuser'
    # Filter model_list by those who have a owner field
    new_list = []
    for model in model_list:
        try:
            model._meta.get_field('owner')
            new_list.append(model)
        except:
            pass
    cursor = connections['old'].cursor()
    cursor.execute(sql_query)
    crmuser_list = dictfetchall(cursor)
    user_list = User.objects.filter(
        id__in=[crmuser['user_id'] for crmuser in crmuser_list])
    sql_query = 'SELECT * FROM'
    for crmuser in crmuser_list:
        user = User.objects.get(id=crmuser.get('user_id'))
        for model in new_list:
            new_query = model.objects.filter(owner=user)
            old_query = model.objects.raw(
                sql_query + ' {} WHERE owner_id={}'.format(model._meta.db_table, crmuser['id'])).using('old')
            if new_query.count() != count(old_query):
                logging.warning('Integrity fault at {} at user {} crmuser {}'.format(model, user, crmuser))


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        app = get_app('alm_crm')
        model_list = get_models(app)
        model_list = filter(lambda(x):issubclass(x,SubscriptionObject), model_list)
        check_object_count(model_list)
        check_objects_by_subscription(model_list)
        check_objects_by_owner(model_list)



