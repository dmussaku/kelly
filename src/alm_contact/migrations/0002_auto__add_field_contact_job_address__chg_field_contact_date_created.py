# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contact.job_address'
        db.add_column('alma_contact', 'job_address',
                      self.gf('alm_contact.fields.AddressField')(default='######Kazakhstan', max_length=200, blank=True),
                      keep_default=False)


        # Changing field 'Contact.date_created'
        db.alter_column('alma_contact', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    def backwards(self, orm):
        # Deleting field 'Contact.job_address'
        db.delete_column('alma_contact', 'job_address')


        # Changing field 'Contact.date_created'
        db.alter_column('alma_contact', 'date_created', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        u'alm_contact.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_address': ('alm_contact.fields.AddressField', [], {'max_length': '200', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'})
        }
    }

    complete_apps = ['alm_contact']