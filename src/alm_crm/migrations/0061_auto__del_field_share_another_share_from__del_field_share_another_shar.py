# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Share.another_share_from'
        db.delete_column('alma_share', 'another_share_from_id')

        # Deleting field 'Share.another_share_to'
        db.delete_column('alma_share', 'another_share_to_id')

        # Adding field 'Share.share_to'
        db.add_column('alma_share', 'share_to',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='in_shares', null=True, to=orm['alm_user.User']),
                      keep_default=False)

        # Adding field 'Share.share_from'
        db.add_column('alma_share', 'share_from',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_shares', null=True, to=orm['alm_user.User']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Share.another_share_from'
        db.add_column('alma_share', 'another_share_from',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_shares_x', null=True, to=orm['alm_user.User']),
                      keep_default=False)

        # Adding field 'Share.another_share_to'
        db.add_column('alma_share', 'another_share_to',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='in_shares_x', null=True, to=orm['alm_user.User']),
                      keep_default=False)

        # Deleting field 'Share.share_to'
        db.delete_column('alma_share', 'share_to_id')

        # Deleting field 'Share.share_from'
        db.delete_column('alma_share', 'share_from_id')


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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'to': u"orm['alm_user.User']"})
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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_owner'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['alm_crm.Contact']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '30'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'alm_crm.crmuser': {
            'Meta': {'object_name': 'CRMUser'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_supervisor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'unfollow_list': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'unfollowers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.Contact']"}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'alm_crm.customfield': {
            'Meta': {'object_name': 'CustomField', 'db_table': "'alma_custom_fields'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        u'alm_crm.hashtag': {
            'Meta': {'object_name': 'HashTag', 'db_table': "'alma_hashtag'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'})
        },
        u'alm_crm.hashtagreference': {
            'Meta': {'object_name': 'HashTagReference', 'db_table': "'alma_hashtag_reference'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hashtag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'references'", 'to': u"orm['alm_crm.HashTag']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_crm.productgroup': {
            'Meta': {'object_name': 'ProductGroup', 'db_table': "'alma_product_group'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_product_groups'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'product_groups'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.Product']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'alm_crm.salescycle': {
            'Meta': {'object_name': 'SalesCycle', 'db_table': "'alma_sales_cycle'"},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sales_cycles'", 'to': u"orm['alm_crm.Contact']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'follow_sales_cycles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['alm_crm.CRMUser']"}),
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
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log'", 'to': u"orm['alm_crm.SalesCycle']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'sales_cycle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'product_stats'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['alm_crm.SalesCycle']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'share_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'in_shares'", 'null': 'True', 'to': u"orm['alm_user.User']"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'salary': ('django.db.models.fields.CharField', [], {'default': "'instant'", 'max_length': '7'}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alm_user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'alma_user'"},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_supervisor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Asia/Almaty'"}),
            'unfollow_list': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['alm_crm.Contact']", 'null': 'True', 'blank': 'True'}),
            'userpic': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alm_crm']