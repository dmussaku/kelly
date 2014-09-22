# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CRMUser'
        db.create_table(u'alm_crm_crmuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('organization_id', self.gf('django.db.models.fields.IntegerField')()),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')()),
            ('is_supervisor', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alm_crm', ['CRMUser'])

        # Adding model 'Contact'
        db.create_table('alma_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=30)),
            ('tp', self.gf('django.db.models.fields.CharField')(default='user', max_length=30)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'], null=True, blank=True)),
            ('company_contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='user_contacts', null=True, to=orm['alm_crm.Contact'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contact_latest_activity', unique=True, null=True, on_delete=models.SET_NULL, to=orm['alm_crm.Activity'])),
        ))
        db.send_create_signal(u'alm_crm', ['Contact'])

        # Adding M2M table for field followers on 'Contact'
        m2m_table_name = db.shorten_name('alma_contact_followers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'alm_crm.contact'], null=False)),
            ('crmuser', models.ForeignKey(orm[u'alm_crm.crmuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'crmuser_id'])

        # Adding M2M table for field assignees on 'Contact'
        m2m_table_name = db.shorten_name('alma_contact_assignees')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'alm_crm.contact'], null=False)),
            ('crmuser', models.ForeignKey(orm[u'alm_crm.crmuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'crmuser_id'])

        # Adding model 'Value'
        db.create_table('alma_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('salary', self.gf('django.db.models.fields.CharField')(default='instant', max_length=7)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
        ))
        db.send_create_signal(u'alm_crm', ['Value'])

        # Adding model 'Product'
        db.create_table('alma_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('company_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'alm_crm', ['Product'])

        # Adding model 'SalesCycle'
        db.create_table('alma_sales_cycle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_sales_cycles', to=orm['alm_crm.CRMUser'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='sales_cycles', on_delete=models.SET_DEFAULT, to=orm['alm_crm.Contact'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Activity'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('projected_value', self.gf('django.db.models.fields.related.OneToOneField')(related_name='_unused_1_sales_cycle', unique=True, null=True, to=orm['alm_crm.Value'])),
            ('real_value', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_unused_2_sales_cycle', unique=True, null=True, to=orm['alm_crm.Value'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=2)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('from_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('to_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['SalesCycle'])

        # Adding M2M table for field products on 'SalesCycle'
        m2m_table_name = db.shorten_name('alma_sales_cycle_products')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('salescycle', models.ForeignKey(orm[u'alm_crm.salescycle'], null=False)),
            ('product', models.ForeignKey(orm[u'alm_crm.product'], null=False))
        ))
        db.create_unique(m2m_table_name, ['salescycle_id', 'product_id'])

        # Adding M2M table for field followers on 'SalesCycle'
        m2m_table_name = db.shorten_name('alma_sales_cycle_followers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('salescycle', models.ForeignKey(orm[u'alm_crm.salescycle'], null=False)),
            ('crmuser', models.ForeignKey(orm[u'alm_crm.crmuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['salescycle_id', 'crmuser_id'])

        # Adding model 'Activity'
        db.create_table('alma_activity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rel_activities', to=orm['alm_crm.SalesCycle'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity_author', to=orm['alm_crm.CRMUser'])),
        ))
        db.send_create_signal(u'alm_crm', ['Activity'])

        # Adding model 'Feedback'
        db.create_table(u'alm_crm_feedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('status', self.gf('django.db.models.fields.CharField')(default='', max_length=1)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('activity', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Activity'], unique=True)),
            ('value', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Value'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Feedback'])

        # Adding model 'Mention'
        db.create_table(u'alm_crm_mention', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'alm_crm', ['Mention'])

        # Adding model 'Comment'
        db.create_table(u'alm_crm_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comment_author', to=orm['alm_crm.CRMUser'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'CRMUser'
        db.delete_table(u'alm_crm_crmuser')

        # Deleting model 'Contact'
        db.delete_table('alma_contact')

        # Removing M2M table for field followers on 'Contact'
        db.delete_table(db.shorten_name('alma_contact_followers'))

        # Removing M2M table for field assignees on 'Contact'
        db.delete_table(db.shorten_name('alma_contact_assignees'))

        # Deleting model 'Value'
        db.delete_table('alma_value')

        # Deleting model 'Product'
        db.delete_table('alma_product')

        # Deleting model 'SalesCycle'
        db.delete_table('alma_sales_cycle')

        # Removing M2M table for field products on 'SalesCycle'
        db.delete_table(db.shorten_name('alma_sales_cycle_products'))

        # Removing M2M table for field followers on 'SalesCycle'
        db.delete_table(db.shorten_name('alma_sales_cycle_followers'))

        # Deleting model 'Activity'
        db.delete_table('alma_activity')

        # Deleting model 'Feedback'
        db.delete_table(u'alm_crm_feedback')

        # Deleting model 'Mention'
        db.delete_table(u'alm_crm_mention')

        # Deleting model 'Comment'
        db.delete_table(u'alm_crm_comment')


    models = {
        u'alm_crm.activity': {
            'Meta': {'object_name': 'Activity', 'db_table': "'alma_activity'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_author'", 'to': u"orm['alm_crm.CRMUser']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_activities'", 'to': u"orm['alm_crm.SalesCycle']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'alm_crm.comment': {
            'Meta': {'object_name': 'Comment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_author'", 'to': u"orm['alm_crm.CRMUser']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'alm_crm.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'assignees': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'assigned_contacts'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.CRMUser']"}),
            'company_contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_contacts'", 'null': 'True', 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'following_contacts'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.CRMUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact_latest_activity'", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.Activity']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '30'}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '30'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']", 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.crmuser': {
            'Meta': {'object_name': 'CRMUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_supervisor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'activity': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Activity']", 'unique': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1'}),
            'value': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Value']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.mention': {
            'Meta': {'object_name': 'Mention'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'alma_product'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.salescycle': {
            'Meta': {'object_name': 'SalesCycle', 'db_table': "'alma_sales_cycle'"},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'sales_cycles'", 'on_delete': 'models.SET_DEFAULT', 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'follow_sales_cycles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.CRMUser']"}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Activity']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_sales_cycles'", 'to': u"orm['alm_crm.CRMUser']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sales_cycles'", 'symmetrical': 'False', 'to': u"orm['alm_crm.Product']"}),
            'projected_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'_unused_1_sales_cycle'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Value']"}),
            'real_value': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_unused_2_sales_cycle'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Value']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '2'}),
            'to_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'alm_crm.value': {
            'Meta': {'object_name': 'Value', 'db_table': "'alma_value'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'salary': ('django.db.models.fields.CharField', [], {'default': "'instant'", 'max_length': '7'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alm_crm']