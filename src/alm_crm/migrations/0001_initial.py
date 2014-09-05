# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contact'
        db.create_table('alma_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vcard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_vcard.VCard'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=30)),
            ('tp', self.gf('django.db.models.fields.CharField')(default='user', max_length=30)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('job_address', self.gf('alm_crm.fields.AddressField')(max_length=200, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=30)),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contact_latest_activity', unique=True, null=True, to=orm['alm_crm.Activity'])),
        ))
        db.send_create_signal(u'alm_crm', ['Contact'])

        # Adding model 'Value'
        db.create_table('alma_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('salary', self.gf('django.db.models.fields.CharField')(default='instant', max_length=7)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
        ))
        db.send_create_signal(u'alm_crm', ['Value'])

        # Adding model 'SalesCycle'
        db.create_table('alma_sales_cycle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='salescycle_owner', to=orm['alm_user.User'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_crm.Contact'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(related_name='latest_activity', unique=True, null=True, to=orm['alm_crm.Activity'])),
            ('project_value', self.gf('django.db.models.fields.related.OneToOneField')(related_name='sales_cycle_project_value', unique=True, to=orm['alm_crm.Value'])),
            ('real_value', self.gf('django.db.models.fields.related.OneToOneField')(related_name='sales_cycle_real_value', unique=True, to=orm['alm_crm.Value'])),
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
            ('product', models.ForeignKey(orm[u'almanet.product'], null=False))
        ))
        db.create_unique(m2m_table_name, ['salescycle_id', 'product_id'])

        # Adding M2M table for field followers on 'SalesCycle'
        m2m_table_name = db.shorten_name('alma_sales_cycle_followers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('salescycle', models.ForeignKey(orm[u'alm_crm.salescycle'], null=False)),
            ('user', models.ForeignKey(orm[u'alm_user.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['salescycle_id', 'user_id'])

        # Adding model 'Activity'
        db.create_table('alma_activity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='', max_length=1)),
            ('feedback', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity_sales_cycle', to=orm['alm_crm.SalesCycle'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity_author', to=orm['alm_user.User'])),
        ))
        db.send_create_signal(u'alm_crm', ['Activity'])

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
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comment_author', to=orm['alm_user.User'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Comment'])

        # Adding M2M table for field followers on 'Goal'
        m2m_table_name = db.shorten_name('alma_goal_followers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('goal', models.ForeignKey(orm[u'alm_crm.goal'], null=False)),
            ('user', models.ForeignKey(orm[u'alm_user.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['goal_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'Contact'
        db.delete_table('alma_contact')

        # Deleting model 'Value'
        db.delete_table('alma_value')

        # Deleting model 'SalesCycle'
        db.delete_table('alma_sales_cycle')

        # Removing M2M table for field products on 'SalesCycle'
        db.delete_table(db.shorten_name('alma_sales_cycle_products'))

        # Removing M2M table for field followers on 'SalesCycle'
        db.delete_table(db.shorten_name('alma_sales_cycle_followers'))

        # Deleting model 'Activity'
        db.delete_table('alma_activity')

        # Deleting model 'Mention'
        db.delete_table(u'alm_crm_mention')

        # Deleting model 'Comment'
        db.delete_table(u'alm_crm_comment')

        # Removing M2M table for field followers on 'Goal'
        db.delete_table(db.shorten_name('alma_goal_followers'))


    models = {
        u'alm_company.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'alma_company'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'owned_company'", 'symmetrical': 'False', 'to': u"orm['alm_user.User']"}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
        u'alm_crm.activity': {
            'Meta': {'object_name': 'Activity', 'db_table': "'alma_activity'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_author'", 'to': u"orm['alm_user.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'feedback': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_sales_cycle'", 'to': u"orm['alm_crm.SalesCycle']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'alm_crm.comment': {
            'Meta': {'object_name': 'Comment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_author'", 'to': u"orm['alm_user.User']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'alm_crm.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '30'}),
            'vcard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_vcard.VCard']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact_latest_activity'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Activity']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '30'})
        },
        u'alm_crm.mention': {
            'Meta': {'object_name': 'Mention'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.salescycle': {
            'Meta': {'object_name': 'SalesCycle', 'db_table': "'alma_sales_cycle'"},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sales_cycle_followers'", 'symmetrical': 'False', 'to': u"orm['alm_user.User']"}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'latest_activity'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Activity']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'salescycle_owner'", 'to': u"orm['alm_user.User']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sales_cycle_product'", 'symmetrical': 'False', 'to': u"orm['almanet.Product']"}),
            'project_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'sales_cycle_project_value'", 'unique': 'True', 'to': u"orm['alm_crm.Value']"}),
            'real_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'sales_cycle_real_value'", 'unique': 'True', 'to': u"orm['alm_crm.Value']"}),
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
