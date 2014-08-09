# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'User.city'
        db.delete_column('alma_user', 'city')

        # Deleting field 'User.country'
        db.delete_column('alma_user', 'country')

        # Adding field 'User.timezone'
        db.add_column('alma_user', 'timezone',
                      self.gf('timezone_field.fields.TimeZoneField')(default='Asia/Almaty'),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'User.city'
        db.add_column('alma_user', 'city',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=30),
                      keep_default=False)

        # Adding field 'User.country'
        db.add_column('alma_user', 'country',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=30),
                      keep_default=False)

        # Deleting field 'User.timezone'
        db.delete_column('alma_user', 'timezone')


    models = {
        u'alm_company.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'alma_company'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'owned_company'", 'symmetrical': 'False', 'to': u"orm['alm_user.User']"}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
        u'alm_user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'alma_user'"},
            'company': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users'", 'symmetrical': 'False', 'to': u"orm['alm_company.Company']"}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Asia/Almaty'"})
        }
    }

    complete_apps = ['alm_user']