# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Payment'
        db.create_table(u'alm_company_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['alm_company.Plan'])),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['alm_company.Company'])),
            ('tp', self.gf('django.db.models.fields.CharField')(default='CARD', max_length=20)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_to_pay', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('date_paid', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('bank_statement', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_company.BankStatement'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'alm_company', ['Payment'])

        # Adding model 'BankStatement'
        db.create_table(u'alm_company_bankstatement', (
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
        db.send_create_signal(u'alm_company', ['BankStatement'])

        # Adding model 'Plan'
        db.create_table(u'alm_company_plan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('users_num', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('contacts_num', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('space_per_user', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'alm_company', ['Plan'])

        # Adding field 'Company.plan'
        db.add_column('alma_company', 'plan',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='companies', null=True, on_delete=models.SET_NULL, to=orm['alm_company.Plan']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Payment'
        db.delete_table(u'alm_company_payment')

        # Deleting model 'BankStatement'
        db.delete_table(u'alm_company_bankstatement')

        # Deleting model 'Plan'
        db.delete_table(u'alm_company_plan')

        # Deleting field 'Company.plan'
        db.delete_column('alma_company', 'plan_id')


    models = {
        u'alm_company.bankstatement': {
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
        u'alm_company.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'alma_company'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'companies'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_company.Plan']"}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
        u'alm_company.payment': {
            'Meta': {'object_name': 'Payment'},
            'bank_statement': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_company.BankStatement']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['alm_company.Company']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_paid': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'date_to_pay': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['alm_company.Plan']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'CARD'", 'max_length': '20'})
        },
        u'alm_company.plan': {
            'Meta': {'object_name': 'Plan'},
            'contacts_num': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'space_per_user': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'users_num': ('django.db.models.fields.IntegerField', [], {'default': '10'})
        }
    }

    complete_apps = ['alm_company']