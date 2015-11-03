# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Plan.name'
        db.delete_column(u'almanet_plan', 'name')

        # Deleting field 'Plan.description'
        db.delete_column(u'almanet_plan', 'description')

        # Adding field 'Plan.name_ru'
        db.add_column(u'almanet_plan', 'name_ru',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Plan.description_ru'
        db.add_column(u'almanet_plan', 'description_ru',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Adding field 'Plan.name_en'
        db.add_column(u'almanet_plan', 'name_en',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Plan.description_en'
        db.add_column(u'almanet_plan', 'description_en',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Adding field 'Plan.price_kzt'
        db.add_column(u'almanet_plan', 'price_kzt',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Plan.price_usd'
        db.add_column(u'almanet_plan', 'price_usd',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Plan.name'
        db.add_column(u'almanet_plan', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Plan.description'
        db.add_column(u'almanet_plan', 'description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Deleting field 'Plan.name_ru'
        db.delete_column(u'almanet_plan', 'name_ru')

        # Deleting field 'Plan.description_ru'
        db.delete_column(u'almanet_plan', 'description_ru')

        # Deleting field 'Plan.name_en'
        db.delete_column(u'almanet_plan', 'name_en')

        # Deleting field 'Plan.description_en'
        db.delete_column(u'almanet_plan', 'description_en')

        # Deleting field 'Plan.price_kzt'
        db.delete_column(u'almanet_plan', 'price_kzt')

        # Deleting field 'Plan.price_usd'
        db.delete_column(u'almanet_plan', 'price_usd')


    models = {
        u'alm_company.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'alma_company'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
        u'alm_user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'alma_user'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'ru-RU'", 'max_length': '30'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Asia/Almaty'"}),
            'userpic_obj': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'users'", 'to': u"orm['almastorage.SwiftFile']"}),
            'vcard': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_vcard.VCard']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
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
        u'almanet.bankstatement': {
            'BANK_NAME': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'BANK_SIGN_CERT_ID': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'BANK_SIGN_TYPE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'CUSTOMER_MAIL': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'CUSTOMER_NAME': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'CUSTOMER_PHONE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'CUSTOMER_SIGN_TYPE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'DEPARTMENT_AMOUNT': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'DEPARTMENT_MERCHANT_ID': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'LETTER': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'MERCHANT_CERT_ID': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'MERCHANT_NAME': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'MERCHANT_SIGN_TYPE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'Meta': {'object_name': 'BankStatement'},
            'ORDER_AMOUNT': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'ORDER_CURRENCY': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'ORDER_ID': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'PAYMENT_AMOUNT': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'PAYMENT_APPROVAL_CODE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'PAYMENT_MERCHANT_ID': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'PAYMENT_REFERENCE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'PAYMENT_RESPONSE_CODE': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'RAWSIGN': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'RESULTS_TIMESTAMP': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'SIGN': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'almanet.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'bank_statement': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['almanet.BankStatement']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_paid': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_to_pay': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['almanet.Plan']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['almanet.Subscription']"}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'CARD'", 'max_length': '20'})
        },
        u'almanet.plan': {
            'Meta': {'object_name': 'Plan'},
            'contacts_num': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'description_en': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'description_ru': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_ru': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price_kzt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price_usd': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'space_per_user': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'users_num': ('django.db.models.fields.IntegerField', [], {'default': '10'})
        },
        u'almanet.service': {
            'Meta': {'object_name': 'Service', 'db_table': "'alma_service'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'almanet.subscription': {
            'Meta': {'object_name': 'Subscription', 'db_table': "'alma_subscription'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': u"orm['alm_company.Company']"}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subscriptions'", 'null': 'True', 'to': u"orm['almanet.Plan']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': u"orm['almanet.Service']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': u"orm['alm_user.User']"})
        },
        u'almastorage.swiftcontainer': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'SwiftContainer', 'db_table': "'sw_container'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service_slug': ('django.db.models.fields.CharField', [], {'default': "'ALMASALES'", 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Main_container'", 'max_length': '255'})
        },
        u'almastorage.swiftfile': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'SwiftFile', 'db_table': "'sw_file'"},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['almastorage.SwiftContainer']"}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 10, 22, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'temp_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['almanet']