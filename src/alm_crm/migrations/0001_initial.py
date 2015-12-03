# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Milestone'
        db.create_table('alma_milestone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('is_system', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('color_code', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Milestone'])

        # Adding model 'Contact'
        db.create_table('alma_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=30)),
            ('tp', self.gf('django.db.models.fields.CharField')(default='user', max_length=30)),
            ('vcard', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contact', null=True, on_delete=models.SET_NULL, to=orm['alm_vcard.VCard'], blank=True, unique=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, on_delete=models.SET_NULL, to=orm['alm_crm.Contact'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_contacts', null=True, to=orm['alm_user.User'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contact_latest_activity', unique=True, null=True, on_delete=models.SET_NULL, to=orm['alm_crm.Activity'])),
            ('import_task', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='contacts', null=True, on_delete=models.SET_NULL, to=orm['alm_crm.ImportTask'])),
        ))
        db.send_create_signal(u'alm_crm', ['Contact'])

        # Adding model 'Value'
        db.create_table('alma_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('salary', self.gf('django.db.models.fields.CharField')(default='instant', max_length=7)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_values', null=True, to=orm['alm_user.User'])),
        ))
        db.send_create_signal(u'alm_crm', ['Value'])

        # Adding model 'Product'
        db.create_table('alma_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(default='KZT', max_length=3)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='crm_products', null=True, to=orm['alm_user.User'])),
        ))
        db.send_create_signal(u'alm_crm', ['Product'])

        # Adding model 'ProductGroup'
        db.create_table('alma_product_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_product_groups', null=True, to=orm['alm_user.User'])),
        ))
        db.send_create_signal(u'alm_crm', ['ProductGroup'])

        # Adding M2M table for field products on 'ProductGroup'
        m2m_table_name = db.shorten_name('alma_product_group_products')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('productgroup', models.ForeignKey(orm[u'alm_crm.productgroup'], null=False)),
            ('product', models.ForeignKey(orm[u'alm_crm.product'], null=False))
        ))
        db.create_unique(m2m_table_name, ['productgroup_id', 'product_id'])

        # Adding model 'SalesCycle'
        db.create_table('alma_sales_cycle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_global', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_sales_cycles', null=True, to=orm['alm_user.User'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sales_cycles', to=orm['alm_crm.Contact'])),
            ('latest_activity', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.Activity'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('projected_value', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='sales_cycle_as_projected', unique=True, null=True, to=orm['alm_crm.Value'])),
            ('real_value', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='sales_cycle_as_real', unique=True, null=True, to=orm['alm_crm.Value'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=2)),
            ('from_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('to_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sales_cycles', null=True, to=orm['alm_crm.Milestone'])),
        ))
        db.send_create_signal(u'alm_crm', ['SalesCycle'])

        # Adding model 'SalesCycleLogEntry'
        db.create_table(u'alm_crm_salescyclelogentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('meta', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log', to=orm['alm_crm.SalesCycle'])),
            ('entry_type', self.gf('django.db.models.fields.CharField')(default='MC', max_length=2)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_logentries', null=True, to=orm['alm_user.User'])),
        ))
        db.send_create_signal(u'alm_crm', ['SalesCycleLogEntry'])

        # Adding model 'Activity'
        db.create_table('alma_activity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_finished', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('need_preparation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rel_activities', to=orm['alm_crm.SalesCycle'])),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity_assignee', null=True, to=orm['alm_user.User'])),
            ('result', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity_owner', null=True, to=orm['alm_user.User'])),
        ))
        db.send_create_signal(u'alm_crm', ['Activity'])

        # Adding model 'ActivityRecipient'
        db.create_table('alma_activity_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipients', to=orm['alm_crm.Activity'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activities', to=orm['alm_user.User'])),
            ('has_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alm_crm', ['ActivityRecipient'])

        # Adding model 'Mention'
        db.create_table(u'alm_crm_mention', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mentions', null=True, to=orm['alm_user.User'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_mentions', null=True, to=orm['alm_user.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'alm_crm', ['Mention'])

        # Adding model 'Comment'
        db.create_table(u'alm_crm_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comment_owner', null=True, to=orm['alm_user.User'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal(u'alm_crm', ['Comment'])

        # Adding model 'CommentRecipient'
        db.create_table('alma_comment_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipients', to=orm['alm_crm.Comment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['alm_user.User'])),
            ('has_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alm_crm', ['CommentRecipient'])

        # Adding model 'AttachedFile'
        db.create_table(u'alm_crm_attachedfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('file_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['almastorage.SwiftFile'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_attachments', null=True, to=orm['alm_user.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['AttachedFile'])

        # Adding model 'Share'
        db.create_table('alma_share', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='share_set', null=True, to=orm['alm_crm.Contact'])),
            ('share_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='in_shares', null=True, to=orm['alm_user.User'])),
            ('share_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_shares', null=True, to=orm['alm_user.User'])),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
        ))
        db.send_create_signal(u'alm_crm', ['Share'])

        # Adding model 'ContactList'
        db.create_table('alma_contact_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_list', null=True, to=orm['alm_user.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('import_task', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['alm_crm.ImportTask'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['ContactList'])

        # Adding M2M table for field contacts on 'ContactList'
        m2m_table_name = db.shorten_name('alma_contact_list_contacts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactlist', models.ForeignKey(orm[u'alm_crm.contactlist'], null=False)),
            ('contact', models.ForeignKey(orm[u'alm_crm.contact'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contactlist_id', 'contact_id'])

        # Adding model 'SalesCycleProductStat'
        db.create_table('alma_cycle_prod_stat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('sales_cycle', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='product_stats', null=True, on_delete=models.SET_NULL, to=orm['alm_crm.SalesCycle'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_crm.Product'])),
            ('real_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('projected_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'alm_crm', ['SalesCycleProductStat'])

        # Adding model 'Filter'
        db.create_table('alma_filter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('filter_text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_filter', null=True, to=orm['alm_user.User'])),
            ('base', self.gf('django.db.models.fields.CharField')(default='all', max_length=6)),
        ))
        db.send_create_signal(u'alm_crm', ['Filter'])

        # Adding model 'HashTag'
        db.create_table('alma_hashtag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'alm_crm', ['HashTag'])

        # Adding unique constraint on 'HashTag', fields ['company_id', 'text']
        db.create_unique('alma_hashtag', ['company_id', 'text'])

        # Adding model 'HashTagReference'
        db.create_table('alma_hashtag_reference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('hashtag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='references', to=orm['alm_crm.HashTag'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'alm_crm', ['HashTagReference'])

        # Adding model 'CustomSection'
        db.create_table('alma_custom_sections', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'alm_crm', ['CustomSection'])

        # Adding model 'CustomField'
        db.create_table('alma_custom_fields', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['CustomField'])

        # Adding model 'CustomFieldValue'
        db.create_table('alma_custom_field_values', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('custom_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['alm_crm.CustomField'])),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['CustomFieldValue'])

        # Adding model 'ImportTask'
        db.create_table(u'alm_crm_importtask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('imported_num', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('not_imported_num', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal(u'alm_crm', ['ImportTask'])

        # Adding model 'ErrorCell'
        db.create_table(u'alm_crm_errorcell', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('import_task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alm_crm.ImportTask'])),
            ('row', self.gf('django.db.models.fields.IntegerField')()),
            ('col', self.gf('django.db.models.fields.IntegerField')()),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal(u'alm_crm', ['ErrorCell'])


    def backwards(self, orm):
        # Removing unique constraint on 'HashTag', fields ['company_id', 'text']
        db.delete_unique('alma_hashtag', ['company_id', 'text'])

        # Deleting model 'Milestone'
        db.delete_table('alma_milestone')

        # Deleting model 'Contact'
        db.delete_table('alma_contact')

        # Deleting model 'Value'
        db.delete_table('alma_value')

        # Deleting model 'Product'
        db.delete_table('alma_product')

        # Deleting model 'ProductGroup'
        db.delete_table('alma_product_group')

        # Removing M2M table for field products on 'ProductGroup'
        db.delete_table(db.shorten_name('alma_product_group_products'))

        # Deleting model 'SalesCycle'
        db.delete_table('alma_sales_cycle')

        # Deleting model 'SalesCycleLogEntry'
        db.delete_table(u'alm_crm_salescyclelogentry')

        # Deleting model 'Activity'
        db.delete_table('alma_activity')

        # Deleting model 'ActivityRecipient'
        db.delete_table('alma_activity_recipient')

        # Deleting model 'Mention'
        db.delete_table(u'alm_crm_mention')

        # Deleting model 'Comment'
        db.delete_table(u'alm_crm_comment')

        # Deleting model 'CommentRecipient'
        db.delete_table('alma_comment_recipient')

        # Deleting model 'AttachedFile'
        db.delete_table(u'alm_crm_attachedfile')

        # Deleting model 'Share'
        db.delete_table('alma_share')

        # Deleting model 'ContactList'
        db.delete_table('alma_contact_list')

        # Removing M2M table for field contacts on 'ContactList'
        db.delete_table(db.shorten_name('alma_contact_list_contacts'))

        # Deleting model 'SalesCycleProductStat'
        db.delete_table('alma_cycle_prod_stat')

        # Deleting model 'Filter'
        db.delete_table('alma_filter')

        # Deleting model 'HashTag'
        db.delete_table('alma_hashtag')

        # Deleting model 'HashTagReference'
        db.delete_table('alma_hashtag_reference')

        # Deleting model 'CustomSection'
        db.delete_table('alma_custom_sections')

        # Deleting model 'CustomField'
        db.delete_table('alma_custom_fields')

        # Deleting model 'CustomFieldValue'
        db.delete_table('alma_custom_field_values')

        # Deleting model 'ImportTask'
        db.delete_table(u'alm_crm_importtask')

        # Deleting model 'ErrorCell'
        db.delete_table(u'alm_crm_errorcell')


    models = {
        u'alm_crm.activity': {
            'Meta': {'object_name': 'Activity', 'db_table': "'alma_activity'"},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_assignee'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need_preparation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_owner'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'result': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rel_activities'", 'to': u"orm['alm_crm.SalesCycle']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.activityrecipient': {
            'Meta': {'object_name': 'ActivityRecipient', 'db_table': "'alma_activity_recipient'"},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipients'", 'to': u"orm['alm_crm.Activity']"}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'has_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'to': u"orm['alm_user.User']"})
        },
        u'alm_crm.attachedfile': {
            'Meta': {'object_name': 'AttachedFile'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'file_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['almastorage.SwiftFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_attachments'", 'null': 'True', 'to': u"orm['alm_user.User']"})
        },
        u'alm_crm.comment': {
            'Meta': {'object_name': 'Comment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_owner'", 'null': 'True', 'to': u"orm['alm_user.User']"})
        },
        u'alm_crm.commentrecipient': {
            'Meta': {'object_name': 'CommentRecipient', 'db_table': "'alma_comment_recipient'"},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipients'", 'to': u"orm['alm_crm.Comment']"}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'has_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['alm_user.User']"})
        },
        u'alm_crm.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_task': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contacts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.ImportTask']"}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact_latest_activity'", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.Activity']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_contacts'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.Contact']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '30'}),
            'tp': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '30'}),
            'vcard': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_vcard.VCard']", 'blank': 'True', 'unique': 'True'})
        },
        u'alm_crm.contactlist': {
            'Meta': {'object_name': 'ContactList', 'db_table': "'alma_contact_list'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contact_list'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_task': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.ImportTask']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_list'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'alm_crm.customfield': {
            'Meta': {'object_name': 'CustomField', 'db_table': "'alma_custom_fields'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.customfieldvalue': {
            'Meta': {'object_name': 'CustomFieldValue', 'db_table': "'alma_custom_field_values'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'custom_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['alm_crm.CustomField']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.customsection': {
            'Meta': {'object_name': 'CustomSection', 'db_table': "'alma_custom_sections'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.errorcell': {
            'Meta': {'object_name': 'ErrorCell'},
            'col': ('django.db.models.fields.IntegerField', [], {}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_crm.ImportTask']"}),
            'row': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.filter': {
            'Meta': {'object_name': 'Filter', 'db_table': "'alma_filter'"},
            'base': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '6'}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'filter_text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_filter'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        u'alm_crm.hashtag': {
            'Meta': {'unique_together': "(('company_id', 'text'),)", 'object_name': 'HashTag', 'db_table': "'alma_hashtag'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'alm_crm.hashtagreference': {
            'Meta': {'object_name': 'HashTagReference', 'db_table': "'alma_hashtag_reference'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hashtag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'references'", 'to': u"orm['alm_crm.HashTag']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.importtask': {
            'Meta': {'object_name': 'ImportTask'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_num': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'not_imported_num': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.mention': {
            'Meta': {'object_name': 'Mention'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_mentions'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mentions'", 'null': 'True', 'to': u"orm['alm_user.User']"})
        },
        u'alm_crm.milestone': {
            'Meta': {'object_name': 'Milestone', 'db_table': "'alma_milestone'"},
            'color_code': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_system': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'alma_product'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'crm_products'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'price': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.productgroup': {
            'Meta': {'object_name': 'ProductGroup', 'db_table': "'alma_product_group'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_product_groups'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'product_groups'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.Product']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'alm_crm.salescycle': {
            'Meta': {'object_name': 'SalesCycle', 'db_table': "'alma_sales_cycle'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sales_cycles'", 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_activity': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Activity']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sales_cycles'", 'null': 'True', 'to': u"orm['alm_crm.Milestone']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_sales_cycles'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sales_cycles'", 'to': u"orm['alm_crm.Product']", 'through': u"orm['alm_crm.SalesCycleProductStat']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'projected_value': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'sales_cycle_as_projected'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Value']"}),
            'real_value': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'sales_cycle_as_real'", 'unique': 'True', 'null': 'True', 'to': u"orm['alm_crm.Value']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'alm_crm.salescyclelogentry': {
            'Meta': {'object_name': 'SalesCycleLogEntry'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'entry_type': ('django.db.models.fields.CharField', [], {'default': "'MC'", 'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_logentries'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log'", 'to': u"orm['alm_crm.SalesCycle']"})
        },
        u'alm_crm.salescycleproductstat': {
            'Meta': {'object_name': 'SalesCycleProductStat', 'db_table': "'alma_cycle_prod_stat'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alm_crm.Product']"}),
            'projected_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'real_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'product_stats'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.SalesCycle']"})
        },
        u'alm_crm.share': {
            'Meta': {'object_name': 'Share', 'db_table': "'alma_share'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'share_set'", 'null': 'True', 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'share_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_shares'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'share_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'in_shares'", 'null': 'True', 'to': u"orm['alm_user.User']"})
        },
        u'alm_crm.value': {
            'Meta': {'object_name': 'Value', 'db_table': "'alma_value'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'KZT'", 'max_length': '3'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_values'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'salary': ('django.db.models.fields.CharField', [], {'default': "'instant'", 'max_length': '7'})
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