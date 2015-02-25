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
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('organization_id', self.gf('django.db.models.fields.IntegerField')()),
            ('is_supervisor', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alm_crm', ['CRMUser'])

        # Adding M2M table for field unfollow_list on 'CRMUser'
        m2m_table_name = db.shorten_name(u'alm_crm_crmuser_unfollow_list')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('crmuser', models.ForeignKey(orm[u'alm_crm.crmuser'], null=False)),
            ('contact', models.ForeignKey(orm[u'alm_crm.contact'], null=False))
        ))
        db.create_unique(m2m_table_name, ['crmuser_id', 'contact_id'])

        # Adding model 'Contact'
        db.create_table('alma_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=30)),
            ('tp', self.gf('django.db.models.fields.CharField')(default='user', max_length=30)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('vcard', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_vcard.VCard'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['alm_crm.Contact'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_contacts', null=True, to=orm['alm_crm.CRMUser'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contact_latest_activity', unique=True, null=True, on_delete=models.SET_NULL, to=orm['alm_crm.Activity'])),
        ))
        db.send_create_signal(u'alm_crm', ['Contact'])

        # Adding model 'Value'
        db.create_table('alma_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('salary', self.gf('django.db.models.fields.CharField')(default='instant', max_length=7)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_values', null=True, to=orm['alm_crm.CRMUser'])),
        ))
        db.send_create_signal(u'alm_crm', ['Value'])

        # Adding model 'Product'
        db.create_table('alma_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='crm_products', null=True, to=orm['alm_crm.CRMUser'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Product'])

        # Adding model 'SalesCycle'
        db.create_table('alma_sales_cycle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_global', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_sales_cycles', to=orm['alm_crm.CRMUser'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sales_cycles', to=orm['alm_crm.Contact'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Activity'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('projected_value', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='sales_cycle_as_projected', unique=True, null=True, to=orm['alm_crm.Value'])),
            ('real_value', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='sales_cycle_as_real', unique=True, null=True, to=orm['alm_crm.Value'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=2)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('from_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('to_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['SalesCycle'])

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
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rel_activities', to=orm['alm_crm.SalesCycle'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity_owner', to=orm['alm_crm.CRMUser'])),
        ))
        db.send_create_signal(u'alm_crm', ['Activity'])

        # Adding model 'ActivityRecipient'
        db.create_table('alma_activity_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipients', to=orm['alm_crm.Activity'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activities', to=orm['alm_crm.CRMUser'])),
            ('has_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alm_crm', ['ActivityRecipient'])

        # Adding model 'Feedback'
        db.create_table(u'alm_crm_feedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('feedback', self.gf('django.db.models.fields.CharField')(max_length=300, null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='W', max_length=1)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('activity', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Activity'], unique=True)),
            ('value', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Value'], unique=True, null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='feedback_owner', to=orm['alm_crm.CRMUser'])),
        ))
        db.send_create_signal(u'alm_crm', ['Feedback'])

        # Adding model 'Mention'
        db.create_table(u'alm_crm_mention', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mentions', null=True, to=orm['alm_crm.CRMUser'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_mentions', null=True, to=orm['alm_crm.CRMUser'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Mention'])

        # Adding model 'Comment'
        db.create_table(u'alm_crm_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comment_owner', to=orm['alm_crm.CRMUser'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal(u'alm_crm', ['Comment'])

        # Adding model 'Share'
        db.create_table('alma_share', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='share_set', null=True, to=orm['alm_crm.Contact'])),
            ('share_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='in_shares', to=orm['alm_crm.CRMUser'])),
            ('share_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_shares', to=orm['alm_crm.CRMUser'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Share'])

        # Adding model 'ContactList'
        db.create_table('alma_contact_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_list', null=True, to=orm['alm_crm.CRMUser'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['ContactList'])

        # Adding M2M table for field users on 'ContactList'
        m2m_table_name = db.shorten_name('alma_contact_list_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactlist', models.ForeignKey(orm[u'alm_crm.contactlist'], null=False)),
            ('crmuser', models.ForeignKey(orm[u'alm_crm.crmuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contactlist_id', 'crmuser_id'])

        # Adding model 'SalesCycleProductStat'
        db.create_table('alma_cycle_prod_stat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_crm.SalesCycle'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_crm.Product'])),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'alm_crm', ['SalesCycleProductStat'])

        # Adding model 'Filter'
        db.create_table('alma_filter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('filter_text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_filter', to=orm['alm_crm.CRMUser'])),
            ('base', self.gf('django.db.models.fields.CharField')(default='all', max_length=6)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Filter'])

        # Adding model 'HashTag'
        db.create_table('alma_hashtag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500)),
        ))
        db.send_create_signal(u'alm_crm', ['HashTag'])

        # Adding model 'HashTagReference'
        db.create_table('alma_hashtag_reference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('hashtag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='references', to=orm['alm_crm.HashTag'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['HashTagReference'])


    def backwards(self, orm):
        # Deleting model 'CRMUser'
        db.delete_table(u'alm_crm_crmuser')

        # Removing M2M table for field unfollow_list on 'CRMUser'
        db.delete_table(db.shorten_name(u'alm_crm_crmuser_unfollow_list'))

        # Deleting model 'Contact'
        db.delete_table('alma_contact')

        # Deleting model 'Value'
        db.delete_table('alma_value')

        # Deleting model 'Product'
        db.delete_table('alma_product')

        # Deleting model 'SalesCycle'
        db.delete_table('alma_sales_cycle')

        # Removing M2M table for field followers on 'SalesCycle'
        db.delete_table(db.shorten_name('alma_sales_cycle_followers'))

        # Deleting model 'Activity'
        db.delete_table('alma_activity')

        # Deleting model 'ActivityRecipient'
        db.delete_table('alma_activity_recipient')

        # Deleting model 'Feedback'
        db.delete_table(u'alm_crm_feedback')

        # Deleting model 'Mention'
        db.delete_table(u'alm_crm_mention')

        # Deleting model 'Comment'
        db.delete_table(u'alm_crm_comment')

        # Deleting model 'Share'
        db.delete_table('alma_share')

        # Deleting model 'ContactList'
        db.delete_table('alma_contact_list')

        # Removing M2M table for field users on 'ContactList'
        db.delete_table(db.shorten_name('alma_contact_list_users'))

        # Deleting model 'SalesCycleProductStat'
        db.delete_table('alma_cycle_prod_stat')

        # Deleting model 'Filter'
        db.delete_table('alma_filter')

        # Deleting model 'HashTag'
        db.delete_table('alma_hashtag')

        # Deleting model 'HashTagReference'
        db.delete_table('alma_hashtag_reference')


    models = {
        u'alm_crm.activity': {
            'Meta': {'object_name': 'Activity', 'db_table': "'alma_activity'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_owner'", 'to': u"orm['alm_crm.CRMUser']"}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_activities'", 'to': u"orm['alm_crm.SalesCycle']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.activityrecipient': {
            'Meta': {'object_name': 'ActivityRecipient', 'db_table': "'alma_activity_recipient'"},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipients'", 'to': u"orm['alm_crm.Activity']"}),
            'has_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'to': u"orm['alm_crm.CRMUser']"})
        },
        u'alm_crm.comment': {
            'Meta': {'object_name': 'Comment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_owner'", 'to': u"orm['alm_crm.CRMUser']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact_latest_activity'", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.Activity']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_contacts'", 'null': 'True', 'to': u"orm['alm_crm.CRMUser']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['alm_crm.Contact']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '30'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '30'}),
            'vcard': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_vcard.VCard']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'alm_crm.contactlist': {
            'Meta': {'object_name': 'ContactList', 'db_table': "'alma_contact_list'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_list'", 'null': 'True', 'to': u"orm['alm_crm.CRMUser']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contact_list'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.CRMUser']"})
        },
        u'alm_crm.crmuser': {
            'Meta': {'object_name': 'CRMUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_supervisor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'unfollow_list': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'unfollowers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.Contact']"}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'activity': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Activity']", 'unique': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feedback_owner'", 'to': u"orm['alm_crm.CRMUser']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Value']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.filter': {
            'Meta': {'object_name': 'Filter', 'db_table': "'alma_filter'"},
            'base': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '6'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filter_text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_filter'", 'to': u"orm['alm_crm.CRMUser']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        u'alm_crm.hashtag': {
            'Meta': {'object_name': 'HashTag', 'db_table': "'alma_hashtag'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'})
        },
        u'alm_crm.hashtagreference': {
            'Meta': {'object_name': 'HashTagReference', 'db_table': "'alma_hashtag_reference'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hashtag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'references'", 'to': u"orm['alm_crm.HashTag']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.mention': {
            'Meta': {'object_name': 'Mention'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_mentions'", 'null': 'True', 'to': u"orm['alm_crm.CRMUser']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mentions'", 'null': 'True', 'to': u"orm['alm_crm.CRMUser']"})
        },
        u'alm_crm.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'alma_product'"},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'crm_products'", 'null': 'True', 'to': u"orm['alm_crm.CRMUser']"}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.salescycle': {
            'Meta': {'object_name': 'SalesCycle', 'db_table': "'alma_sales_cycle'"},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sales_cycles'", 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'follow_sales_cycles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.CRMUser']"}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Activity']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_sales_cycles'", 'to': u"orm['alm_crm.CRMUser']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sales_cycles'", 'to': u"orm['alm_crm.Product']", 'through': u"orm['alm_crm.SalesCycleProductStat']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'projected_value': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'sales_cycle_as_projected'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Value']"}),
            'real_value': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'sales_cycle_as_real'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Value']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '2'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'alm_crm.salescycleproductstat': {
            'Meta': {'object_name': 'SalesCycleProductStat', 'db_table': "'alma_cycle_prod_stat'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_crm.Product']"}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_crm.SalesCycle']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'alm_crm.share': {
            'Meta': {'object_name': 'Share', 'db_table': "'alma_share'"},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'share_set'", 'null': 'True', 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'share_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_shares'", 'to': u"orm['alm_crm.CRMUser']"}),
            'share_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'in_shares'", 'to': u"orm['alm_crm.CRMUser']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.value': {
            'Meta': {'object_name': 'Value', 'db_table': "'alma_value'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_values'", 'null': 'True', 'to': u"orm['alm_crm.CRMUser']"}),
            'salary': ('django.db.models.fields.CharField', [], {'default': "'instant'", 'max_length': '7'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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