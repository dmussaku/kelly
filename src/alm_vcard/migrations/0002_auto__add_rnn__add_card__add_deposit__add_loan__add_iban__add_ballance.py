# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Rnn'
        db.create_table(u'alm_vcard_rnn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Rnn'])

        # Adding model 'Card'
        db.create_table(u'alm_vcard_card', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('ballance', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('history', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal(u'alm_vcard', ['Card'])

        # Adding model 'Deposit'
        db.create_table(u'alm_vcard_deposit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('apr', self.gf('django.db.models.fields.FloatField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_finished', self.gf('django.db.models.fields.DateTimeField')()),
            ('deposit_sum', self.gf('django.db.models.fields.IntegerField')()),
            ('payment_history', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal(u'alm_vcard', ['Deposit'])

        # Adding model 'Loan'
        db.create_table(u'alm_vcard_loan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('apr', self.gf('django.db.models.fields.FloatField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_finished', self.gf('django.db.models.fields.DateTimeField')()),
            ('loan_sum', self.gf('django.db.models.fields.IntegerField')()),
            ('left_sum', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('payment_history', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal(u'alm_vcard', ['Loan'])

        # Adding model 'IBAN'
        db.create_table(u'alm_vcard_iban', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['IBAN'])

        # Adding model 'Ballance'
        db.create_table(u'alm_vcard_ballance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('ballance', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Ballance'])


    def backwards(self, orm):
        # Deleting model 'Rnn'
        db.delete_table(u'alm_vcard_rnn')

        # Deleting model 'Card'
        db.delete_table(u'alm_vcard_card')

        # Deleting model 'Deposit'
        db.delete_table(u'alm_vcard_deposit')

        # Deleting model 'Loan'
        db.delete_table(u'alm_vcard_loan')

        # Deleting model 'IBAN'
        db.delete_table(u'alm_vcard_iban')

        # Deleting model 'Ballance'
        db.delete_table(u'alm_vcard_ballance')


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
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_finished': ('django.db.models.fields.DateTimeField', [], {}),
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
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_finished': ('django.db.models.fields.DateTimeField', [], {}),
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