# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BankStatement'
        db.create_table(u'almanet_bankstatement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('BANK_NAME', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('CUSTOMER_NAME', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('CUSTOMER_MAIL', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('CUSTOMER_PHONE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('MERCHANT_CERT_ID', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('MERCHANT_NAME', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('ORDER_ID', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('ORDER_AMOUNT', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('ORDER_CURRENCY', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('DEPARTMENT_MERCHANT_ID', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('DEPARTMENT_AMOUNT', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('MERCHANT_SIGN_TYPE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('CUSTOMER_SIGN_TYPE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('RESULTS_TIMESTAMP', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('PAYMENT_MERCHANT_ID', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('PAYMENT_AMOUNT', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('PAYMENT_REFERENCE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('PAYMENT_APPROVAL_CODE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('PAYMENT_RESPONSE_CODE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('BANK_SIGN_CERT_ID', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('BANK_SIGN_TYPE', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('LETTER', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('SIGN', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('RAWSIGN', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal(u'almanet', ['BankStatement'])

        # Adding model 'Plan'
        db.create_table(u'almanet_plan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('users_num', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('contacts_num', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('space_per_user', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'almanet', ['Plan'])

        # Adding model 'Payment'
        db.create_table(u'almanet_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['almanet.Subscription'])),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['almanet.Plan'])),
            ('tp', self.gf('django.db.models.fields.CharField')(default='CARD', max_length=20)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_to_pay', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_paid', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('bank_statement', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['almanet.BankStatement'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'almanet', ['Payment'])

        # Adding field 'Subscription.plan'
        db.add_column('alma_subscription', 'plan',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subscriptions', null=True, to=orm['almanet.Plan']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'BankStatement'
        db.delete_table(u'almanet_bankstatement')

        # Deleting model 'Plan'
        db.delete_table(u'almanet_plan')

        # Deleting model 'Payment'
        db.delete_table(u'almanet_payment')

        # Deleting field 'Subscription.plan'
        db.delete_column('alma_subscription', 'plan_id')


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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 10, 21, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'temp_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['almanet']