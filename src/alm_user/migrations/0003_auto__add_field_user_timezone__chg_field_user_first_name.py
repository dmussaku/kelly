# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'User.timezone'
        db.add_column('alma_user', 'timezone',
                      self.gf('timezone_field.fields.TimeZoneField')(default='America/Los_Angeles'),
                      keep_default=False)


        # Changing field 'User.first_name'
        db.alter_column('alma_user', 'first_name', self.gf('django.db.models.fields.CharField')(max_length=31))

    def backwards(self, orm):
        # Deleting field 'User.timezone'
        db.delete_column('alma_user', 'timezone')


        # Changing field 'User.first_name'
        db.alter_column('alma_user', 'first_name', self.gf('django.db.models.fields.CharField')(max_length=30))

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
            'timezone': ('timezone_field.fields.TimeZoneField', [], {})
        }
    }

    complete_apps = ['alm_user']