# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'User.city'
        db.add_column('alma_user', 'city',
                      self.gf('django.db.models.fields.CharField')(default='Almaty', max_length=30),
                      keep_default=False)

        # Adding field 'User.country'
        db.add_column('alma_user', 'country',
                      self.gf('django.db.models.fields.CharField')(default='Kazakhstan', max_length=30),
                      keep_default=False)

        # Adding field 'User.subdomain'
        db.add_column('alma_user', 'subdomain',
                      self.gf('django.db.models.fields.CharField')(default='subdomain', max_length=300),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'User.city'
        db.delete_column('alma_user', 'city')

        # Deleting field 'User.country'
        db.delete_column('alma_user', 'country')

        # Deleting field 'User.subdomain'
        db.delete_column('alma_user', 'subdomain')


    models = {
        u'alm_user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'alma_user'"},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['alm_user']