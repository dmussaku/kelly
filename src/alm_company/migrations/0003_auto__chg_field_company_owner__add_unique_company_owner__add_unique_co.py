# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Company.owner'
        db.alter_column('alma_company', 'owner_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['alm_user.User']))
        # Adding unique constraint on 'Company', fields ['owner']
        db.create_unique('alma_company', ['owner_id'])

        # Adding unique constraint on 'Company', fields ['subdomain']
        db.create_unique('alma_company', ['subdomain'])


    def backwards(self, orm):
        # Removing unique constraint on 'Company', fields ['subdomain']
        db.delete_unique('alma_company', ['subdomain'])

        # Removing unique constraint on 'Company', fields ['owner']
        db.delete_unique('alma_company', ['owner_id'])


        # Changing field 'Company.owner'
        db.alter_column('alma_company', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_user.User']))

    models = {
        u'alm_company.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'alma_company'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'owned_company'", 'unique': 'True', 'to': u"orm['alm_user.User']"}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
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
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['alm_company']
