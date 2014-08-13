# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Goal.product'
        db.add_column('alma_goal', 'product',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=1, related_name='goal_product', unique=True, to=orm['almanet.Product']),
                      keep_default=False)

        # Adding field 'Goal.assignee'
        db.add_column('alma_goal', 'assignee',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=2, related_name='goal_assignee', to=orm['alm_user.User']),
                      keep_default=False)

        # Adding field 'Goal.contact'
        db.add_column('alma_goal', 'contact',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=2, to=orm['alm_crm.Contact'], unique=True),
                      keep_default=False)

        # Adding field 'Goal.project_value'
        db.add_column('alma_goal', 'project_value',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=2, related_name='goal_project_value', unique=True, to=orm['alm_crm.Value']),
                      keep_default=False)

        # Adding field 'Goal.real_value'
        db.add_column('alma_goal', 'real_value',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=2, related_name='goal_real_value', unique=True, to=orm['alm_crm.Value']),
                      keep_default=False)

        # Adding M2M table for field followers on 'Goal'
        m2m_table_name = db.shorten_name('alma_goal_followers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('goal', models.ForeignKey(orm[u'alm_crm.goal'], null=False)),
            ('user', models.ForeignKey(orm[u'alm_user.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['goal_id', 'user_id'])


    def backwards(self, orm):
        # Deleting field 'Goal.product'
        db.delete_column('alma_goal', 'product_id')

        # Deleting field 'Goal.assignee'
        db.delete_column('alma_goal', 'assignee_id')

        # Deleting field 'Goal.contact'
        db.delete_column('alma_goal', 'contact_id')

        # Deleting field 'Goal.project_value'
        db.delete_column('alma_goal', 'project_value_id')

        # Deleting field 'Goal.real_value'
        db.delete_column('alma_goal', 'real_value_id')

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
        u'alm_crm.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "'alma_contact'"},
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'})
        },
        u'alm_crm.goal': {
            'Meta': {'object_name': 'Goal', 'db_table': "'alma_goal'"},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'goal_assignee'", 'to': u"orm['alm_user.User']"}),
            'contact': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['alm_crm.Contact']", 'unique': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'goal_followers'", 'symmetrical': 'False', 'to': u"orm['alm_user.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goal_product'", 'unique': 'True', 'to': u"orm['almanet.Product']"}),
            'project_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goal_project_value'", 'unique': 'True', 'to': u"orm['alm_crm.Value']"}),
            'real_value': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goal_real_value'", 'unique': 'True', 'to': u"orm['alm_crm.Value']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '2'})
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
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Asia/Almaty'"})
        },
        u'almanet.product': {
            'Meta': {'object_name': 'Product', 'db_table': "'alma_product'"},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alm_crm']