# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Payment.date_to_pay'
        db.alter_column(u'alm_company_payment', 'date_to_pay', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Payment.date_paid'
        db.alter_column(u'alm_company_payment', 'date_paid', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'Payment.date_to_pay'
        db.alter_column(u'alm_company_payment', 'date_to_pay', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 10, 20, 0, 0)))

        # Changing field 'Payment.date_paid'
        db.alter_column(u'alm_company_payment', 'date_paid', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 10, 20, 0, 0)))

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
            'date_paid': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_to_pay': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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