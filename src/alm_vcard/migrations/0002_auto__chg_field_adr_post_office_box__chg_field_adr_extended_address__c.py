# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Adr.post_office_box'
        db.alter_column(u'alm_vcard_adr', 'post_office_box', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Adr.extended_address'
        db.alter_column(u'alm_vcard_adr', 'extended_address', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Adr.locality'
        db.alter_column(u'alm_vcard_adr', 'locality', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Adr.region'
        db.alter_column(u'alm_vcard_adr', 'region', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Adr.postal_code'
        db.alter_column(u'alm_vcard_adr', 'postal_code', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Adr.country_name'
        db.alter_column(u'alm_vcard_adr', 'country_name', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Adr.street_address'
        db.alter_column(u'alm_vcard_adr', 'street_address', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

    def backwards(self, orm):

        # Changing field 'Adr.post_office_box'
        db.alter_column(u'alm_vcard_adr', 'post_office_box', self.gf('django.db.models.fields.CharField')(default='', max_length=1024))

        # Changing field 'Adr.extended_address'
        db.alter_column(u'alm_vcard_adr', 'extended_address', self.gf('django.db.models.fields.CharField')(default='', max_length=1024))

        # Changing field 'Adr.locality'
        db.alter_column(u'alm_vcard_adr', 'locality', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024))

        # Changing field 'Adr.region'
        db.alter_column(u'alm_vcard_adr', 'region', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024))

        # Changing field 'Adr.postal_code'
        db.alter_column(u'alm_vcard_adr', 'postal_code', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024))

        # Changing field 'Adr.country_name'
        db.alter_column(u'alm_vcard_adr', 'country_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024))

        # Changing field 'Adr.street_address'
        db.alter_column(u'alm_vcard_adr', 'street_address', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024))

    models = {
        u'alm_vcard.adr': {
            'Meta': {'object_name': 'Adr'},
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'extended_address': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locality': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'post_office_box': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adrs'", 'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.agent': {
            'Meta': {'object_name': 'Agent'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.category': {
            'Meta': {'object_name': 'Category'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.email': {
            'Meta': {'object_name': 'Email'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'emails'", 'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.geo': {
            'Meta': {'object_name': 'Geo'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': u"orm['alm_vcard.VCard']"})
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
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tels'", 'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.title': {
            'Meta': {'object_name': 'Title'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'titles'", 'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.tz': {
            'Meta': {'object_name': 'Tz'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.url': {
            'Meta': {'object_name': 'Url'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'value': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urls'", 'to': u"orm['alm_vcard.VCard']"})
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