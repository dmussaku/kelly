# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Deposit.date_finished'
        db.alter_column(u'alm_vcard_deposit', 'date_finished', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Loan.date_finished'
        db.alter_column(u'alm_vcard_loan', 'date_finished', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'Deposit.date_finished'
        db.alter_column(u'alm_vcard_deposit', 'date_finished', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 10, 28, 0, 0)))

        # Changing field 'Loan.date_finished'
        db.alter_column(u'alm_vcard_loan', 'date_finished', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 10, 28, 0, 0)))

    models = {
        u'alm_vcard.adr': {
            'Meta': {'object_name': 'Adr'},
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'extended_address': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locality': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'post_office_box': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.agent': {
            'Meta': {'object_name': 'Agent'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.ballance': {
            'Meta': {'object_name': 'Ballance'},
            'ballance': ('django.db.models.fields.IntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.card': {
            'Meta': {'object_name': 'Card'},
            'ballance': ('django.db.models.fields.IntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'history': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.category': {
            'Meta': {'object_name': 'Category'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.deposit': {
            'Meta': {'object_name': 'Deposit'},
            'apr': ('django.db.models.fields.FloatField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'deposit_sum': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'payment_history': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.email': {
            'Meta': {'object_name': 'Email'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.geo': {
            'Meta': {'object_name': 'Geo'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.iban': {
            'Meta': {'object_name': 'IBAN'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.key': {
            'Meta': {'object_name': 'Key'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.label': {
            'Meta': {'object_name': 'Label'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.loan': {
            'Meta': {'object_name': 'Loan'},
            'apr': ('django.db.models.fields.FloatField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_sum': ('django.db.models.fields.IntegerField', [], {}),
            'loan_sum': ('django.db.models.fields.IntegerField', [], {}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'payment_history': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.mailer': {
            'Meta': {'object_name': 'Mailer'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.nickname': {
            'Meta': {'object_name': 'Nickname'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.note': {
            'Meta': {'object_name': 'Note'},
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.org': {
            'Meta': {'object_name': 'Org'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'organization_unit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.rnn': {
            'Meta': {'object_name': 'Rnn'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.role': {
            'Meta': {'object_name': 'Role'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.tel': {
            'Meta': {'object_name': 'Tel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.title': {
            'Meta': {'object_name': 'Title'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.tz': {
            'Meta': {'object_name': 'Tz'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.url': {
            'Meta': {'object_name': 'Url'},
            'data': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
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
        }
    }

    complete_apps = ['alm_vcard']