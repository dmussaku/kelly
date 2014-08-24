# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contact.company_contact'
        db.add_column('alma_contact', 'company_contact',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='user_contacts', null=True, to=orm['alm_crm.Contact']),
                      keep_default=False)


        # Changing field 'Contact.vcard'
        db.alter_column('alma_contact', 'vcard_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'], null=True))

    def backwards(self, orm):
        # Deleting field 'Contact.company_contact'
        db.delete_column('alma_contact', 'company_contact_id')


        # Changing field 'Contact.vcard'
        db.alter_column('alma_contact', 'vcard_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['alm_vcard.VCard']))

    models = {
        u'alm_company.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'alma_company'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'owned_company'", 'symmetrical': 'False', 'to': u"orm['alm_user.User']"}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
        u'alm_crm.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'company_contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_contacts'", 'null': 'True', 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '30'}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '30'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']", 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.goal': {
            'Meta': {'object_name': 'Goal', 'db_table': "'alma_goal'"},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'goal_assignee'", 'to': u"orm['alm_user.User']"}),
            'contact': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Contact']", 'unique': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'goal_followers'", 'symmetrical': 'False', 'to': u"orm['alm_user.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goal_product'", 'unique': 'True', 'to': u"orm['almanet.Product']"}),
            'project_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goal_project_value'", 'unique': 'True', 'to': u"orm['alm_crm.Value']"}),
            'real_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goal_real_value'", 'unique': 'True', 'to': u"orm['alm_crm.Value']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '2'})
        },
        u'alm_crm.value': {
            'Meta': {'object_name': 'Value', 'db_table': "'alma_value'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'salary': ('django.db.models.fields.CharField', [], {'default': "'instant'", 'max_length': '7'})
        },
        u'alm_user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'alma_user'"},
            'company': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users'", 'symmetrical': 'False', 'to': u"orm['alm_company.Company']"}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Asia/Almaty'"})
        },
        u'alm_vcard.vcard': {
            'Meta': {'object_name': 'VCard', 'db_table': "'alma_vcard'"},
            'additional_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'classP': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'fn': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'given_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'honorific_prefix': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'honorific_suffix': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rev': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sort_string': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'almanet.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'alma_product'"},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alm_crm']