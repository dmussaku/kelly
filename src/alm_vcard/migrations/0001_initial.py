# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VCard'
        db.create_table('alma_vcard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fn', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('family_name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('given_name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('additional_name', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('honorific_prefix', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('honorific_suffix', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('bday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('classP', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('rev', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('sort_string', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_vcard', ['VCard'])

        # Adding model 'Tel'
        db.create_table(u'alm_vcard_tel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Tel'])

        # Adding model 'Email'
        db.create_table(u'alm_vcard_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('value', self.gf('django.db.models.fields.EmailField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Email'])

        # Adding model 'Geo'
        db.create_table(u'alm_vcard_geo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal(u'alm_vcard', ['Geo'])

        # Adding model 'Org'
        db.create_table(u'alm_vcard_org', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('organization_name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('organization_unit', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal(u'alm_vcard', ['Org'])

        # Adding model 'Adr'
        db.create_table(u'alm_vcard_adr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('post_office_box', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('extended_address', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('street_address', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('locality', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('country_name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal(u'alm_vcard', ['Adr'])

        # Adding model 'Agent'
        db.create_table(u'alm_vcard_agent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Agent'])

        # Adding model 'Category'
        db.create_table(u'alm_vcard_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Category'])

        # Adding model 'Key'
        db.create_table(u'alm_vcard_key', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Key'])

        # Adding model 'Label'
        db.create_table(u'alm_vcard_label', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal(u'alm_vcard', ['Label'])

        # Adding model 'Mailer'
        db.create_table(u'alm_vcard_mailer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal(u'alm_vcard', ['Mailer'])

        # Adding model 'Nickname'
        db.create_table(u'alm_vcard_nickname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Nickname'])

        # Adding model 'Note'
        db.create_table(u'alm_vcard_note', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'alm_vcard', ['Note'])

        # Adding model 'Role'
        db.create_table(u'alm_vcard_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Role'])

        # Adding model 'Title'
        db.create_table(u'alm_vcard_title', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Title'])

        # Adding model 'Tz'
        db.create_table(u'alm_vcard_tz', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'alm_vcard', ['Tz'])

        # Adding model 'Url'
        db.create_table(u'alm_vcard_url', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('data', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'alm_vcard', ['Url'])


    def backwards(self, orm):
        # Deleting model 'VCard'
        db.delete_table('alma_vcard')

        # Deleting model 'Tel'
        db.delete_table(u'alm_vcard_tel')

        # Deleting model 'Email'
        db.delete_table(u'alm_vcard_email')

        # Deleting model 'Geo'
        db.delete_table(u'alm_vcard_geo')

        # Deleting model 'Org'
        db.delete_table(u'alm_vcard_org')

        # Deleting model 'Adr'
        db.delete_table(u'alm_vcard_adr')

        # Deleting model 'Agent'
        db.delete_table(u'alm_vcard_agent')

        # Deleting model 'Category'
        db.delete_table(u'alm_vcard_category')

        # Deleting model 'Key'
        db.delete_table(u'alm_vcard_key')

        # Deleting model 'Label'
        db.delete_table(u'alm_vcard_label')

        # Deleting model 'Mailer'
        db.delete_table(u'alm_vcard_mailer')

        # Deleting model 'Nickname'
        db.delete_table(u'alm_vcard_nickname')

        # Deleting model 'Note'
        db.delete_table(u'alm_vcard_note')

        # Deleting model 'Role'
        db.delete_table(u'alm_vcard_role')

        # Deleting model 'Title'
        db.delete_table(u'alm_vcard_title')

        # Deleting model 'Tz'
        db.delete_table(u'alm_vcard_tz')

        # Deleting model 'Url'
        db.delete_table(u'alm_vcard_url')


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
        u'alm_vcard.category': {
            'Meta': {'object_name': 'Category'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"})
        },
        u'alm_vcard.org': {
            'Meta': {'object_name': 'Org'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'organization_unit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
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