# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from alm_crm.models import SalesCycle

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for sales_cycle in orm['alm_crm.SalesCycle'].objects.all():
            try:
                if sales_cycle.is_global == True and sales_cycle.contact == None:
                    sales_cycle.delete()
            except:
                continue

        for contact in orm['alm_crm.Contact'].objects.all():
            try:
                sales_cycle_count = contact.sales_cycles.filter(is_global=True).count()
                if sales_cycle_count < 1:
                    SalesCycle.create_globalcycle(
                        **{'subscription_id':contact.subscription_id,
                         'owner_id':contact.owner_id,
                         'contact_id':contact.id
                        }
                        )
            except:
                SalesCycle.create_globalcycle(
                    **{'subscription_id':contact.subscription_id,
                     'owner_id':contact.owner_id,
                     'contact_id':contact.id
                    }
                    )
            finally:
                sales_cycles = contact.sales_cycles.filter(is_global=True)
                if len(sales_cycles) > 1:
                    for sc in sales_cycles[1:]:
                        for a in sc.get_activities():
                            sales_cycles[0].rel_activities.add(a)
                        sc.delete()



    def backwards(self, orm):
        "Write your backwards methods here."
        # raise RuntimeError("Couldn't reverse this migration")

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
    symmetrical = True
