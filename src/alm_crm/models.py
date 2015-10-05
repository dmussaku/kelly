# -*- coding: utf-8 -*-

import functools
import os
from django.db import models, transaction, IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from almanet.utils.metaprogramming import DirtyFieldsMixin
from almanet.models import SubscriptionObject, Subscription
from alm_company.models import Company
from alm_vcard.models import (
    VCard,
    BadVCardError,
    Org,
    Title,
    Tel,
    Email,
    Category,
    Adr,
    Url,
    Note,
    )
from alm_user.models import User, Account
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.db.models import signals, Q
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete, pre_delete
from django.utils import timezone
from datetime import datetime, timedelta
import xlrd
import pytz
import time
from django.conf import settings
TEMP_DIR = getattr(settings, 'TEMP_DIR')

from alm_vcard import models as vcard_models
from celery import group, Task, result
import json
from almanet.utils.cache import build_key, extract_id
from almanet.utils.json import date_handler
# from .tasks import create_failed_contacts_xls

ALLOWED_TIME_PERIODS = ['week', 'month', 'year']

CURRENCY_OPTIONS = (
    ('USD', 'US Dollar'),
    ('RUB', 'Rubbles'),
    ('KZT', 'Tenge'),
)

GLOBAL_CYCLE_TITLE = u'Основной поток'
GLOBAL_CYCLE_DESCRIPTION = u'Автоматически созданный цикл'

def type_cast(input):
    return input if type(input) != float else str(input)

class Milestone(SubscriptionObject):

    title = models.CharField(_("title"), max_length=1024, null=True, blank=True)
    is_system = models.IntegerField(default=0)
    color_code = models.CharField(_('color code'), max_length=1024, null=True, blank=True)
    sort = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('milestone')
        db_table = settings.DB_PREFIX.format('milestone')

    @classmethod
    def create_default_milestones(cls, company_id):
        milestones = []
        default_data = [{'title':u'Звонок/Заявка', 'color_code': '#F4B59C', 'is_system':0, 'sort':1},
                        {'title':u'Отправка КП', 'color_code': '#F59CC8', 'is_system':0, 'sort':2},
                        {'title':u'Согласование договора', 'color_code': '#A39CF4', 'is_system':0, 'sort':3},
                        {'title':u'Выставление счета', 'color_code': '#9CE5F4', 'is_system':0, 'sort':4},
                        {'title':u'Контроль оплаты', 'color_code': '#9CF4A7', 'is_system':0, 'sort':5},
                        {'title':u'Предоставление услуги', 'color_code': '#D4F49B', 'is_system':0, 'sort':6},
                        {'title':u'Upsales', 'color_code': '#F4DC9C', 'is_system':0, 'sort':7},
                        {'title':u'Успешно завершено', 'color_code':'#9CF4A7', 'is_system':1, 'sort':8},
                        {'title':u'Не реализовано', 'color_code':'#F4A09C', 'is_system':2, 'sort':9}]

        for data in default_data:
            milestone = Milestone()
            milestone.title = data['title']
            milestone.color_code = data['color_code']
            milestone.is_system = data['is_system']
            milestone.sort = data['sort']
            milestone.company_id = company_id
            milestone.save()
            milestones.append(milestone)

        return milestones

    def __unicode__(self):
        return '%s'%self.title


class Contact(SubscriptionObject):
    STATUSES_CAPS = (
        _('new_contact'),
        _('lead_contact'),
        _('opportunity_contact'),
        _('client_contact'))
    STATUSES = (NEW, LEAD, OPPORTUNITY, CLIENT) = range(len(STATUSES_CAPS))
    STATUSES_OPTIONS = zip(STATUSES, STATUSES_CAPS)
    STATUSES_DICT = dict(zip(('NEW', 'LEAD', 'OPPORTUNITY', 'CLIENT'), STATUSES))

    TYPES = (COMPANY_TP, USER_TP) = ('co', 'user')
    TYPES_OPTIONS = ((COMPANY_TP, _('company type')),
                     (USER_TP, _('user type')))
    TYPES_DICT = dict(zip(('COMPANY', 'USER'), TYPES))

    SHARE_IMPORTED_TEXT = _('Imported at ')

    status = models.IntegerField(
        _('contact status'),
        max_length=30,
        choices=STATUSES_OPTIONS, default=NEW)
    tp = models.CharField(
        _('contact type'),
        max_length=30,
        choices=TYPES_OPTIONS, default=USER_TP)
    vcard = models.OneToOneField('alm_vcard.VCard', blank=True, null=True,
                                 on_delete=models.SET_NULL, related_name='contact')
    parent = models.ForeignKey(
        'Contact', blank=True, null=True, related_name='children')
    owner = models.ForeignKey(
        User, related_name='owned_contacts',
        null=True)
    latest_activity = models.OneToOneField(
        'Activity', on_delete=models.SET_NULL,
        related_name='contact_latest_activity', null=True)
    mentions = generic.GenericRelation('Mention')
    comments = generic.GenericRelation('Comment')
    import_task = models.ForeignKey(
        'ImportTask', blank=True, null=True, related_name='contacts', on_delete=models.SET_NULL)
    custom_field_values = generic.GenericRelation('CustomFieldValue')

    class Meta:
        verbose_name = _('contact')
        db_table = settings.DB_PREFIX.format('contact')

    def __unicode__(self):
        try:
            return u"%s %s" % (self.vcard.fn, self.tp)
        except:
            return "No name %s" % self.tp

    def delete(self):
        if self.vcard:
            self.vcard.delete()
        super(self.__class__, self).delete()

    @property
    def last_contacted(self):
        return self.latest_activity and self.latest_activity.date_created

    @property
    def name(self):
        if not self.vcard:
            return _('Unknown')
        return self.vcard.fn

    def tel(self, type='CELL'):
        if not self.vcard:
            return _('Unknown')
        tel = self.vcard.tel_set.filter(type=type).first().value
        return tel and tel or None

    def mobile(self):
        if not self.tel(type='CELL'):
            return _('Unknown')
        return self.tel(type='CELL')

    def email(self, type='WORK'):
        if not self.vcard:
            return _('Unknown')
        email = self.vcard.email_set.filter(type=type).first().value
        return email and email or None

    def email_work(self):
        return self.email(type='INTERNET')

    def company(self):
        if not self.vcard:
            return _('Unknown organization')
        org = self.vcard.org_set.first()
        if not org:
            return _('Unknown organization')
        return org.name

    def get_tp(self):
        return dict(self.TYPES_OPTIONS).get(self.tp, None)

    def is_new(self):
        return self.status == self.NEW

    def is_lead(self):
        return self.status == self.LEAD

    def is_opportunity(self):
        return self.status == self.OPPORTUNITY

    def is_client(self):
        return self.status == self.CLIENT

    def change_status(self, new_status, save=False):
        """TODO Set status to contact. Return instance (self)"""
        self.status = new_status
        if save:
            self.save()
        return self

    def export_to(self, tp, **options):
        if tp not in ('html', 'vcard'):
            return False
        exporter = getattr(self, 'to_{}'.format(tp))
        return exporter(**options)

    def to_html(self, locale='ru_RU'):
        tpl_name = 'vcard/_detail.%s.html' % locale
        context = {'object': self.vcard}
        return render_to_string(tpl_name, context)

    def find_latest_activity(self):
        """Find latest activity among all sales_cycle_contacts."""
        sales_cycle = self.sales_cycles.order_by('latest_activity__date_created').first()
        latest_activity = None
        try:
            latest_activity = sales_cycle.latest_activity
        except Activity.DoesNotExist:
            return None
        return sales_cycle and latest_activity or None

    def add_mention(self, user_ids=None):
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        build_single_mention = functools.partial(Mention.build_new,
                                                 content_class=self.__class__,
                                                 object_id=self.pk,
                                                 save=True)
        self.mentions = map(build_single_mention, user_ids)
        self.save()

    @classmethod
    def share_contact(cls, share_from, share_to, contact_id, company_id, comment=None):
        return cls.share_contacts(share_from, share_to, [contact_id], company_id, comment)

    @classmethod
    def share_contacts(cls, share_from, share_to, contact_ids, company_id, comment=None):
        '''
        Share multiple contacts to a single user
        '''
        assert isinstance(contact_ids, (list, tuple)), 'Must be a list'
        if not contact_ids:
            return False
        try:
            share_from = User.objects.get(id=share_from)
            share_to = User.objects.get(id=share_to)
            contacts = Contact.objects.filter(id__in=contact_ids)
            share_list = []
            for contact in contacts:
                share = Share(
                        share_from=share_from,
                        share_to=share_to,
                        contact=contact
                    )
                share.company_id = company_id
                share.save()
                share_list.append(share)
            '''
            I do not know how you will submit mentions in comments so i'm leaving
            this blank for now
            '''
            if comment:
                for share in share_list:
                    comment = Comment(
                        comment=comment,
                        object_id=share.id,
                        owner_id=share_from.id,
                        content_type_id=ContentType.objects.get_for_model(Share).id,
                        company_id = company_id
                        )
                    comment.save()
            return True
        except:
            return False

    def create_share_to(self, user_id, company_id, note=None):
        default_note = self.SHARE_IMPORTED_TEXT + \
            self.date_created.strftime(settings.DATETIME_FORMAT_NORMAL)

        share = Share(
            note=note or default_note,
            share_to_id=user_id,
            share_from_id=user_id,
            contact_id=self.id,
            company_id=company_id
        )
        share.save()
        return share

    @classmethod
    def upd_lst_activity_on_create(cls, sender, created=False,
                                   instance=None, **kwargs):
        if not created or instance.sales_cycle.is_global:
            return
        c = instance.sales_cycle.contact
        c.latest_activity = instance
        c.save()

    @classmethod
    def upd_status_when_first_activity_created(cls, sender, created=False,
                                               instance=None, **kwargs):
        if not created or instance.sales_cycle.is_global:
            return
        c = instance.sales_cycle.contact
        if c.status == cls.NEW:
            c.status = cls.LEAD
            c.save()

    @classmethod
    def get_contacts_by_status(cls, company_id, status):
        q = Q(company_id=company_id)
        q &= Q(status=status)
        return Contact.objects.filter(q).order_by('-date_created')

    @classmethod
    def filter_contacts_by_vcard(cls, company_id, search_text,
                                 search_params=None, order_by=None):
        r"""TODO Make a search query for contacts by their vcard.
        Important! Search params have one of the following formats:
            - name of vcard field, if simple field
            - entity.name of vcard related field, if via foreign key

        Parameters
        ---------
            search_text - text by which we execute a search
            search_params - list of vcard fields [
                ('fn', 'startswith'), ('org__organization_unit', 'icontains'), 'bday']
            order_by - sort results by fields e.g. ('-pk', '...')
            limit - how much rows must be returned
            offset - from which row to start
        Returns
        -------
            Queryset<Contact> that found by search
            len(Queryset<Contact>) <= limit
        """
        assert isinstance(search_params, list), "Must be a list"

        def build_params(search_text, search_params):
            POSSIBLE_MODIFIERS = ['startswith', 'icontains']
            rv = {}
            for param in search_params:
                if isinstance(param, tuple):
                    if param[1] not in POSSIBLE_MODIFIERS:
                        raise Exception(_('incorrect modifier'))
                    rv['%s__%s' % param] = search_text
                else:
                    rv[param] = search_text
            return rv

        params = build_params(search_text, search_params)
        contacts = Contact.objects.none()

        for key, value in params.viewitems():
            query_dict = {'vcard__'+str(key): str(value)}
            q = Q(company_id=company_id)
            q &= Q(**query_dict)
            contacts = contacts | Contact.objects.filter(q)

        assert isinstance(order_by, list), "Must be a list"
        if order_by:
            if order_by[1] == 'asc':
                return contacts.order_by('vcard__'+str(order_by[0]))
            else:
                return contacts.order_by('-vcard__'+str(order_by[0]))
        return contacts

    @classmethod
    def get_contact_detail(cls, contact_id, with_vcard=False):
        """TEST Returns contact detail by `contact_id`."""
        c = Contact.objects.filter(pk=contact_id)
        if not with_vcard:
            return c.first()
        c = c.select_related('vcard')
        return c.first()

    @classmethod
    def get_contact_products(cls, contact_id):
        """
            TEST Returns contact products by `contact_id`
            get it from salescycles by contact
        """
        c = Contact.objects.get(pk=contact_id)
        sales_cycle_ids = c.sales_cycles.values_list('pk', flat=True)
        return Product.objects.filter(sales_cycles__pk__in=sales_cycle_ids)

    @classmethod
    def get_contact_activities(cls, contact_id):
        """TEST Returns list of activities ordered by date."""
        c = Contact.objects.get(pk=contact_id)
        sales_cycle_ids = c.sales_cycles.values_list('pk', flat=True)
        return Activity.objects.filter(sales_cycle_id__in=sales_cycle_ids)\
            .order_by('-date_created')

    @classmethod
    def upload_contacts(cls, upload_type, file_obj, save=False):
        """Extracts contacts from source: vcard file or csv file or any
        other file objects. Build queryset from them and save if required.
        Parameters
        ----------
            upload_type  - csv or vcard or ...
            file_obj - file instance"""
        ALLOWED_CONTACT_UPLOAD_TYPES = ('csv', 'vcard')
        assert upload_type in ALLOWED_CONTACT_UPLOAD_TYPES, ""
        upload_handler = getattr(cls, '_upload_contacts_by_%s' % upload_type)
        contacts = upload_handler(file_obj)
        if save:
            contacts.save()
            # SalesCycle.create_globalcycle(
            #         **{'company_id': contacts.company_id,
            #          'owner_id': contacts.owner.id,
            #          'contact_id': contacts.id
            #         }
            #     )
        return contacts

    @classmethod
    def _upload_contacts_by_vcard(cls, vcard_obj):
        """Extracts contacts from vcard string. Returns Queryset<Contact>."""
        contact = cls()
        vcard = VCard.fromVCard(vcard_obj, autocommit=True)
        contact.vcard = vcard
        return contact

    @classmethod
    def import_from_vcard(cls, raw_vcard, creator, company_id):
        """
        Parameters
        ----------
            raw_vcard - serialized repr of vcard
            creator - crm user who owns created objects
        """
        rv = []
        vcards = VCard.importFromVCardMultiple(raw_vcard, autocommit=False)
        with transaction.atomic():
            for vcard in vcards:
                try:
                    vcard.commit()
                except BadVCardError as e:
                    print e
                    continue
                c = cls(vcard=vcard, owner=creator)
                c.company_id = company_id
                c.save()
                SalesCycle.create_globalcycle(
                    **{'company_id': c.company_id,
                     'owner_id': c.owner.id,
                     'contact_id': c.id
                    }
                )

                rv.append(c)
        return rv

    @classmethod
    def import_from_csv(cls, csv_file_data, creator):
        raw_data = csv_file_data.split('\n')
        raw_data = [obj.replace('"','') for obj in raw_data]
        # raw_data = [obj.encode('utf-8') for obj in raw_data]
        fields = raw_data[0].split(';')
        data = []
        for obj in raw_data[1:]:
            data.append(obj.split(';'))
        # print data
        contact_list = []
        for i in range(0, len(data)):
            if len(fields)==len(data[i]):
                c = cls()
                c.owner = creator
                c.company_id = creator.company_id
                v = VCard()
                v.given_name = data[i][0].decode('utf-8')
                # print data[i]
                v.additional_name = data[i][1].decode('utf-8')
                v.family_name = data[i][2].decode('utf-8')
                v.fn = v.given_name+" "+v.family_name
                if not v.fn:
                    continue
                v.save()
                c.vcard = v
                c.save()
                SalesCycle.create_globalcycle(
                        **{'company_id':c.company_id,
                         'owner_id':creator.id,
                         'contact_id':c.id
                        }
                    )
                if data[i][5]:
                    org = Org(vcard=v)
                    org.organization_name = data[i][5].decode('utf-8')
                    org.save()
                if data[i][6]:
                    title = Title(vcard=v)
                    title.data = data[i][6].decode('utf-8')
                    title.save()
                if data[i][7]:
                    tel = Tel(vcard=v, type='cell_phone')
                    tel.value = data[i][7].decode('utf-8')
                    tel.save()
                if data[i][8]:
                    tel = Tel(vcard=v, type='fax')
                    tel.value = data[i][8].decode('utf-8')
                    tel.save()
                if data[i][9]:
                    tel = Tel(vcard=v, type='home')
                    tel.value = data[i][9].decode('utf-8')
                    tel.save()
                if data[i][10]:
                    tel = Tel(vcard=v, type='pager')
                    tel.value = data[i][10].decode('utf-8')
                    tel.save()
                if data[i][11]:
                    tel = Tel(vcard=v, type='INTL')
                    tel.value = data[i][11].decode('utf-8')
                    tel.save()
                if data[i][12]:
                    email = Email(vcard=v, type='internet')
                    email.value = data[i][12].decode('utf-8')
                    email.save()
                if data[i][13]:
                    email = Email(vcard=v, type='x400')
                    email.value = data[i][13].decode('utf-8')
                    email.save()
                if data[i][14]:
                    tel = Tel(vcard=v, type='work')
                    tel.value = data[i][14].decode('utf-8')
                    tel.save()
                if data[i][15]:
                    email = Email(vcard=v, type='pref')
                    email.value = data[i][15].decode('utf-8')
                    email.save()
                contact_list.append(c)
                print "%s created contact %s" % (c, c.id)
                # print contact_list
        return contact_list

    '''
    Creates contact from data which is row from xls file and file_structure
    which has a specific format, here's the example of both 
    file_structure:
    [
        {'num':0, 'model':'VCard', 'attr':'fn'},
        {'num':1, 'model':'Adr', 'attr':'postal'},
        {'num':2, 'model':'Org'},
        {'num':3, 'model':'Email', 'attr':'internet'}
    ]
    data:
    ['John Smith', 'Black water Valley;Chicago;60616;USA;;Home County;Almaty;000100;Kazakhstan',
    'Microsoft', 'sam@gmail.com;at@gmail.com'
    ]

    The result is the response {'error':True/False, 'contact_id':n, 'error_col':m}
    where error is boolean, n and m are integers
    '''

    @classmethod
    def create_from_structure(cls, data, file_structure, creator, import_task, company_id):
        contact = cls()
        vcard = VCard(fn='Без Имени')
        vcard.save()
        response = {}
        for structure_dict in file_structure:
            col_num = int(structure_dict.get('num'))
            model = getattr(vcard_models, structure_dict.get('model'))
            if type(data[col_num].value) == float:
                data[col_num].value = str(data[col_num].value)
            if model == vcard_models.VCard:
                attr = structure_dict.get('attr',"")
                try:
                    if type(data[col_num].value) == unicode:
                        setattr(vcard, attr, data[col_num].value)
                    else:
                        setattr(vcard, attr, str(data[col_num].value))
                    try:
                        vcard.save()
                    except Exception as e:
                        print str(e) + 'at col {} at 589'.format(col_num)
                        pass
                except Exception as e:
                    print str(e) + 'at col {} at 592'.format(col_num)
                    # transaction.savepoint_rollback(sid)
                    try:
                        vcard.delete()
                    except Exception as e:
                        print str(e) + 'at col {} 597'.format(col_num)
                        pass
                    response['error'] = True
                    response['error_col'] = col_num
                    return response
            elif (model == vcard_models.Tel or model == vcard_models.Email 
                        or model == vcard_models.Url):
                try:
                    if data[col_num].value:
                        objects = data[col_num].value.split(';')
                        for object in objects:
                            v_type = structure_dict.get('attr','')
                            obj = model(type=v_type, value = object)
                            obj.vcard = vcard
                            obj.save()
                except Exception as e:
                    print str(e) + 'at col {} at 613'.format(col_num)
                    # transaction.savepoint_rollback(sid)
                    try:
                        vcard.delete()
                    except Exception as e:
                        print str(e) + 'at col {} 618'.format(col_num)
                        pass
                    response['error'] = True
                    response['error_col'] = col_num
                    return response
            elif model == vcard_models.Org:
                try:
                    if data[col_num].value:
                        objects = data[col_num].value.split(';')
                        for object in objects:
                            v_type = structure_dict.get('attr','')
                            obj = model(organization_name = object)
                            obj.vcard = vcard
                            obj.save()
                except Exception as e:
                    print str(e) + 'at col {} at 633'.format(col_num)
                    # transaction.savepoint_rollback(sid)
                    try:
                        vcard.delete()
                    except Exception as e:
                        print str(e) + 'at col {} at 638'.format(col_num)
                        pass
                    response['error'] = True
                    response['error_col'] = col_num
                    return response
            elif model == vcard_models.Adr:
                adr_type = structure_dict.get('attr','')
                try:
                    if data[col_num].value:
                        adresses = type_cast(data[col_num].value).split(';;')
                        for address_str in adresses:
                            addr_objs = address_str.split(';')
                            addr_objs = [vcard, adr_type] + addr_objs
                            address = Adr.create_from_list(addr_objs)
                except Exception as e:
                    print str(e) + 'at col {} at 653'.format(col_num)
                    # transaction.savepoint_rollback(sid)
                    try:
                        vcard.delete()
                    except Exception as e:
                        print str(e) + 'at col {} 658'.format(col_num)
                        pass
                    response['error'] = True
                    response['error_col'] = col_num
                    return response
            elif (model == vcard_models.Geo or model == vcard_models.Agent 
                    or model == vcard_models.Category or model == vcard_models.Key 
                    or model == vcard_models.Label or model == vcard_models.Mailer 
                    or model == vcard_models.Nickname or model == vcard_models.Note 
                    or model == vcard_models.Role or model == vcard_models.Title 
                    or model == vcard_models.Tz):
                try:
                    if data[col_num].value:
                        objects = data[col_num].value.split(';')
                        for object in objects:
                            v_type = structure_dict.get('attr','')
                            obj = model(data = object)
                            obj.vcard = vcard
                            obj.save()
                except Exception as e:
                    print str(e) + 'at col {} at 678'.format(col_num)
                    # transaction.savepoint_rollback(sid)
                    try:
                        vcard.delete()
                    except Exception as e:
                        print str(e) + 'at col {} at 683'.format(col_num)
                        pass
                    response['error'] = True
                    response['error_col'] = col_num
                    return response
        try:
            vcard.save()
        except Exception as e:
            print str(e) + 'at col {} at 691'.format(col_num)
            response['error'] = True
            response['error_col'] = 0
            return response
        if vcard.fn == 'Без Имени' and vcard.org_set.first():
            vcard.fn = vcard.org_set.first().organization_name
            vcard.save()
            contact.tp = 'co'
        elif vcard.fn == 'Без Имени' and vcard.email_set.first():
            vcard.fn = vcard.email_set.first().value
            vcard.save()
        contact.vcard = vcard
        contact.import_task = import_task
        contact.owner = creator
        contact.company_id = company_id
        contact.save()
        SalesCycle.create_globalcycle(
                        **{'company_id':contact.company_id,
                         'owner_id':creator.id,
                         'contact_id':contact.id
                        }
                    )
        return {'error':False, 'contact_id':contact.id}

    @classmethod
    def get_xls_structure(cls, filename, xls_file_data):
        book = xlrd.open_workbook(file_contents=xls_file_data)
        sheet = book.sheets()[0]
        try:
            data=sheet.row(0)
        except:
            return {'success':False}
        ext = filename.split('.')[len(filename.split('.')) - 1]
        new_filename = datetime.now().__str__()
        if not os.path.exists(os.path.join(TEMP_DIR)):
            os.makedirs(TEMP_DIR)
        myfile = open(
            os.path.join(TEMP_DIR, new_filename),
            'wb'
            )
        myfile.write(xls_file_data)
        myfile.close()
        return {
            'success':True,
            'col_num':sheet.ncols,
            'filename':new_filename,
            'contact_list_name':filename,
            'data':[d.value for d in data]
        }

    @classmethod
    def get_contacts_by_last_activity_date(
            cls, company_id, user_id=None, owned=True, mentioned=False,
            in_shares=False, all=False, include_activities=False):
        """TEST Returns list of contacts ordered by last activity date.
            Returns:
                Queryset<Contact>
                if includes:
                    Queryset<Activity>
                    contact_activity_map {1: [2], 3: [4, 5, 6]}
            example: (contacts, activities, contact_activity_map)

            TO: Rustem K (answered)
            probably better structure:
            if include_activities:
                (Queryset<Contact>, Queryset<Activity>, {Contact1: [Activity1, Activity2], Contact2: [Activity3]})
            else:
                Queryset<Contact>
            in this case return value is always instance of dict, so it is easier to process it
            at the same time, list of contacts always available through rv.keys()
        """
        q0 = Q(company_id=company_id)
        q = Q()
        if not all:
            if owned:
                q |= Q(owner_id=user_id)
            if mentioned:
                q |= Q(mentions__user_id=user_id)
            if in_shares:
                user = User.objects.get(pk=user_id)
                shares = user.in_shares
                q |= Q(id__in=set(shares.values_list('contact_id', flat=True)))
        if not all and len(q.children) == 0:
            contacts = cls.objects.none()
        else:
            contacts = cls.objects.filter(q0 & q).order_by(
                '-latest_activity__date_created')

        if not include_activities:
            return contacts

        contact_activity_map = dict()
        sales_cycle_contact_map, sales_cycles_pks = dict(), set([])
        for contact in contacts:
            current_scycles_pks = contact.sales_cycles.values_list('pk', flat=True)
            sales_cycles_pks |= set(current_scycles_pks)
            for current_cycle_pk in current_scycles_pks:
                sales_cycle_contact_map[current_cycle_pk] = contact.pk
        activities = Activity.objects.filter(
            sales_cycle__id__in=sales_cycles_pks).order_by('date_created')
        for activity in activities:
            contact_pk = sales_cycle_contact_map[activity.sales_cycle.pk]
            contact_activity_map.setdefault(contact_pk, []).append(activity.pk)
        return (contacts, activities, contact_activity_map)

    @classmethod
    def get_cold_base(cls, company_id):
        """Returns list of contacts that are considered cold.
        Cold contacts should satisfy two conditions:
            1. no assignee for contact
            2. status is NEW"""
        q = Q(company_id=company_id)
        q &= Q(status=cls.NEW)
        return cls.objects.filter(q).order_by('-date_created')

    def merge_contacts(self, alias_objects=[], delete_merged=True):
        t = time.time()
        if not alias_objects:
            return {'success':False, 'message':'No alias objects appended'}
        for obj in alias_objects:
            if not isinstance(obj, self.__class__):
                return {'success':False, 'message':'Not Instance of Contact'}

        # original_sales_cycles = self.sales_cycles.filter(
        #     is_global=False) 
        # original_activities = [obj.id for obj in Activity.objects.filter(
        #             sales_cycle__in=self.sales_cycles.all())] 
        # original_shares = [ obj.id for obj in self.share_set.all() ]
        global_sales_cycle = SalesCycle.get_global(self.company_id, self.id)
        deleted_sales_cycle_ids = [ obj.sales_cycles.get(is_global=True).id for obj in alias_objects ]
        # Merging sales Cycles
        activities = []
        sales_cycles = []
        shares = []
        try:
            note_data = self.vcard.note_set.last().data
        except:
            note_data = ""
        for obj in alias_objects:
            if obj.vcard.note_set.all():
                note_data += "\n" + obj.vcard.note_set.last().data
        with transaction.atomic():
            for obj in alias_objects:
                for sales_cycle in obj.sales_cycles.all():
                    if sales_cycle.is_global:
                        for activity in sales_cycle.rel_activities.all():
                            activity.sales_cycle = global_sales_cycle
                            activity.save()
                            activities.append(activity)
                    else:
                        sales_cycle.contact = self
                        sales_cycle.save()
                        sales_cycles.append(sales_cycle)
                        # [activities.append(obj) for obj in sales_cycle.rel_activities.all()]

        # Merging vcards
        VCard.merge_model_objects(self.vcard, [c.vcard for c in alias_objects])
        self.vcard.note_set.all().delete()
        if note_data:
            note = Note(data=note_data, vcard=self.vcard)
            note.save()
        #mergin shares
        with transaction.atomic():
            for obj in alias_objects:
                for share in obj.share_set.all():
                    share.contact = self
                    share.save()
                    shares.append(share)
        if delete_merged:
            deleted_contacts = [contact.id for contact in alias_objects]
            alias_objects.delete()
        else:
            deleted_contacts = []
        # sales_cycles = self.sales_cycles.all().exclude(
        #     id__in=original_sales_cycles).prefetch_related('rel_activities')
        # activities = Activity.objects.filter(
        #     sales_cycle__in=self.sales_cycles.all()).exclude(id__in=original_activities)
        # shares = self.share_set.all().exclude(id__in=original_shares)
        response = {
            'success':True,
            'contact':self,
            'deleted_contacts_ids':deleted_contacts,
            'deleted_sales_cycle_ids':deleted_sales_cycle_ids,
            'sales_cycles':sales_cycles,
            'activities':activities,
            'shares':shares,
        }
        # print "Approximate time of merging contacts %s " % str(time.time()-t)
        return response


    @classmethod
    def delete_contacts(cls, obj_ids):
        if isinstance(obj_ids, int):
            obj_ids = [obj_ids]
        assert isinstance(obj_ids, (tuple, list)), "must be a list"
        with transaction.atomic():
            objects = {
                "contacts": [],
                "sales_cycles": [],
                "activities": [],
                "shares": [],
                "does_not_exist": []
            }
            for contact_id in obj_ids:
                try:
                    # print contact_id
                    obj = Contact.objects.get(id=contact_id)
                    objects['contacts'].append(contact_id)
                    objects['sales_cycles'] += list(obj.sales_cycles.all().values_list("id", flat=True))
                    for sales_cycle in obj.sales_cycles.all():
                        objects['activities'] += list(sales_cycle.rel_activities.all().values_list("id", flat=True))
                    objects['shares'] += list(obj.share_set.all().values_list("id", flat=True))
                    obj.delete()
                except ObjectDoesNotExist:
                    objects['does_not_exist'].append(contact_id)
            return objects

    def serialize(self):

        return {
            'author_id': self.owner_id,
            'company_id': self.company_id,
            'custom_fields':{cf.custom_field_id:cf.value for cf in self.custom_field_values.all()},
            'date_created': self.date_created,
            'date_edited': self.date_edited,
            'id': self.pk,
            'pk': self.pk,
            'owner': self.owner_id,
            'parent_id': hasattr(self, 'parent_id') and self.parent_id or None,
            'children': [child.pk for child in self.children.all()],
            'sales_cycles': [cycle.pk for cycle in self.sales_cycles.all()],
            'status': self.status,
            'tp': self.tp,
            'vcard_id': self.vcard_id
        }

    @classmethod
    def after_save(cls, sender, instance, **kwargs):
        cache.set(build_key(cls._meta.model_name, instance.pk), json.dumps(instance.serialize(), default=date_handler))
    
        # TODO: each time when contact is updated vcard is recreated. So if it is the case then reinvalidate cache
        vcard = instance.vcard
        if vcard:
            cache.set(build_key(vcard.__class__._meta.model_name, vcard.id), json.dumps(vcard.serialize(), default=date_handler))
        # vcard_id = vcard.id
        # cached_vcard = cache.get(build_key(vcard.__class__._meta.model_name, vcard_id))
        # if cached_vcard is None:
        #     return
        # cached_vcard = json.loads(cached_vcard)
        # old_id = cached_vcard['vcard_id']
        # cached_vcard['vcard_id'] = instance.pk
        # cache.set(build_key(contact.__class__._meta.model_name, contact_id), json.dumps(cached_vcard))
        # cache.delete(build_key(cls._meta.model_name, old_id))

    @classmethod
    def after_delete(cls, sender, instance, **kwargs):
        cache.delete(build_key(cls._meta.model_name, instance.pk))

    @classmethod
    def get_by_ids(cls, *ids):
        """Get vcard by ids from cache with fallback to postgres."""
        rv = cache.get_many([build_key(cls._meta.model_name, cid) for cid in ids])
        rv = {extract_id(k, coerce=int): json.loads(v) for k, v in rv.iteritems()}

        not_found_ids = [cid for cid in ids if not cid in rv]
        if not not_found_ids:
            return rv.values()
        contact_qs = cls.objects.filter(pk__in=not_found_ids).prefetch_related('sales_cycles', 'children')
        more_rv = list(c.serialize() for c in contact_qs)
        cache.set_many({build_key(cls._meta.model_name, contact_raw['id']): json.dumps(contact_raw, default=date_handler)
                        for contact_raw in more_rv})
        return rv.values() + more_rv

    @classmethod
    def recache(cls, ids):
        if not isinstance(ids, list):
            ids=[ids]
        contact_qs = cls.objects.filter(id__in=ids).prefetch_related('sales_cycles', 'children')
        contact_raws = [c.serialize() for c in contact_qs]
        cache.set_many({build_key(cls._meta.model_name, contact_raw['id']): json.dumps(contact_raw, default=date_handler) for contact_raw in contact_raws})

    @classmethod
    def cache_all(cls):
        contact_qs = cls.objects.all().prefetch_related('sales_cycles', 'children')
        contact_raws = [c.serialize() for c in contact_qs]
        cache.set_many({build_key(cls._meta.model_name, contact_raw['id']): json.dumps(contact_raw, default=date_handler) for contact_raw in contact_raws})


post_save.connect(Contact.after_save, sender=Contact)
post_delete.connect(Contact.after_delete, sender=Contact)


class Value(SubscriptionObject):
    # Type of payment
    SALARY_OPTIONS = (
        ('monthly', 'Monthly'),
        ('annualy', 'Annualy'),
        ('instant', 'Instant'),
    )
    salary = models.CharField(max_length=7, choices=SALARY_OPTIONS,
                              default='instant')
    amount = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS,
                                default='KZT')
    # owner = models.ForeignKey(User, null=True, blank=True,
    #                           related_name='owned_values')

    owner = models.ForeignKey(User, null=True, blank=True,
        related_name='owned_values')

    class Meta:
        verbose_name = 'value'
        db_table = settings.DB_PREFIX.format('value')

    def __unicode__(self):
        return "%s %s %s" % (self.amount, self.currency, self.salary)

    @classmethod
    def get_values(cls, company_id):
        q = Q(company_id=company_id)
        return cls.objects.filter(q)


class Product(SubscriptionObject):
    name = models.CharField(_('product name'), max_length=100, blank=False)
    description = models.TextField(_('product description'))
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS,
                                default='KZT')
    # owner = models.ForeignKey(User, related_name='crm_products',
    #                           null=True, blank=True)
    custom_field_values = generic.GenericRelation('CustomFieldValue')
    owner = models.ForeignKey(User, null=True, blank=True,
        related_name='crm_products')

    class Meta:
        verbose_name = _('product')
        db_table = settings.DB_PREFIX.format('product')

    def __unicode__(self):
        return self.name

    @property
    def author(self):
        return self.owner

    @property
    def author_id(self):
        return self.owner_id

    @author_id.setter
    def author_id(self, author_id):
        self.owner = User.objects.get(id=author_id)

    def add_sales_cycle(self, sales_cycle_id, **kw):
        """TEST Assigns products to salescycle"""
        return self.add_sales_cycles([sales_cycle_id], **kw)

    def add_sales_cycles(self, sales_cycle_ids):
        """TEST Assigns products to salescycle"""
        if isinstance(sales_cycle_ids, int):
            sales_cycle_ids = [sales_cycle_ids]
        assert isinstance(sales_cycle_ids, (tuple, list)), "must be a list"
        sales_cycles = SalesCycle.objects.filter(pk__in=sales_cycle_ids)
        if not sales_cycles:
            return False
        with transaction.atomic():
            for sales_cycle in sales_cycles:
                SalesCycleProductStat.objects.get_or_create(
                    sales_cycle=sales_cycle, product=self)
        return True

    @classmethod
    def get_products(cls, company_id):
        q = Q(company_id=company_id)
        return cls.objects.filter(q).order_by('-date_created')

    @classmethod
    @transaction.atomic()
    def import_from_xls(cls, xls_file_data, creator, company_id):
        '''
        first column is name, second is description and third is price
        '''
        book = xlrd.open_workbook(file_contents=xls_file_data)
        #book = xlrd.open_workbook(filename='medonica_products.xlsx')
        product_list = []
        sheet = book.sheets()[0]
        col_names = [col_name.value for col_name in sheet.row(0)][3:]
        for i in range(1, sheet.nrows):
            row_vals = [val.value for val in sheet.row(i)]
            if not row_vals[0]:
                continue
            product = Product(
                name=row_vals[0],
                company_id=company_id,
                owner=creator
                )
            if row_vals[1]:
                product.description = row_vals[1]
            if row_vals[2]:
                product.price = row_vals[2]
            else:
                product.price = 0
            product.save()
            # for i in range(0, len(row_vals[3:])):
            #     if row_vals[i]:
            #         field = CustomField(title=col_names[i], content_type=ContentType.objects.get_for_model(Product))
            #         field.save()
            #         field_value = CustomFieldValue.build_new(field=field, value=row_vals[i],
            #                                                 object_id=product.id, save=True)
            #         field = CustomField.build_new(
            #             title=col_names[i],
            #             value=row_vals[i],
            #             content_class=Product,
            #             object_id=product.id,
            #             save=True
            #             )
            product_list.append(product)
        return product_list

post_save.connect(VCard.after_save, sender=VCard)

class ProductGroup(SubscriptionObject):
    title = models.CharField(max_length=150)
    products = models.ManyToManyField(Product, related_name='product_groups',
                                   null=True, blank=True)
    owner = models.ForeignKey(User, related_name='owned_product_groups', null=True)

    class Meta:
        verbose_name = _('product_group')
        db_table = settings.DB_PREFIX.format('product_group')

    def __unicode__(self):
        return self.title


class SalesCycle(SubscriptionObject):
    STATUSES_CAPS = (
        _('New'),
        _('Pending'),
        _('Completed'))
    STATUSES = (NEW, PENDING, COMPLETED) = ('N', 'P', 'C')
    STATUSES_OPTIONS = zip(STATUSES, STATUSES_CAPS)
    STATUSES_DICT = dict(zip(('NEW', 'PENDING', 'COMPLETED'), STATUSES))

    is_global = models.BooleanField(default=False)

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    products = models.ManyToManyField(Product, related_name='sales_cycles',
                                      null=True, blank=True,
                                      through='SalesCycleProductStat')
    owner = models.ForeignKey(User, related_name='owned_sales_cycles', null=True)

    contact = models.ForeignKey(Contact, related_name='sales_cycles')
    latest_activity = models.OneToOneField('Activity',
                                           blank=True, null=True,
                                           on_delete=models.SET_NULL)
    projected_value = models.OneToOneField(
        Value, related_name='sales_cycle_as_projected', null=True, blank=True,)
    real_value = models.OneToOneField(
        Value, related_name='sales_cycle_as_real',
        null=True, blank=True,)
    status = models.CharField(max_length=2,
                              choices=STATUSES_OPTIONS, default=NEW)
    from_date = models.DateTimeField(blank=False, auto_now_add=True)
    to_date = models.DateTimeField(blank=False, auto_now_add=True)
    mentions = generic.GenericRelation('Mention')
    comments = generic.GenericRelation('Comment')
    milestone = models.ForeignKey(Milestone, related_name='sales_cycles', null=True)

    class Meta:
        verbose_name = 'sales_cycle'
        db_table = settings.DB_PREFIX.format('sales_cycle')

    def __unicode__(self):
        return '%s [%s %s]' % (self.title, self.contact, self.status)

    def delete(self):
        print 'at salescycle delete'
        super(self.__class__, self).delete()

    @property
    def activities_count(self):
        return self.rel_activities.count()

    @classmethod
    def get_global(cls, company_id, contact_id):
        return SalesCycle.objects.get(company_id=company_id, contact_id=contact_id,
                                      is_global=True)

    def find_latest_activity(self):
        return self.rel_activities.order_by('-date_created').first()

    # Adds mentions to a current class, takes a lsit of user_ids as an input
    # and then runs through the list and calls the function build_new which
    # is declared in Mention class

    @classmethod
    def create_globalcycle(cls, **kwargs):
        try:
            global_cycle = SalesCycle.get_global(contact_id=kwargs['contact_id'],
                                    company_id=kwargs['company_id'])
        except SalesCycle.DoesNotExist:
            global_cycle = cls(
                is_global=True,
                title=GLOBAL_CYCLE_TITLE,
                description=GLOBAL_CYCLE_DESCRIPTION,
                **kwargs)
            global_cycle.save()
        return global_cycle

    def add_mention(self, user_ids=None):
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        build_single_mention = functools.partial(Mention.build_new,
                                                 content_class=self.__class__,
                                                 object_id=self.pk,
                                                 save=True)

        map(self.mentions.add, map(build_single_mention, user_ids))
        self.save()

    def assign_user(self, user_id, save=False):
        """TEST Assign user to salescycle."""
        try:
            self.owner = User.objects.get(id=user_id)
            if save:
                self.save()
            return True
        except User.DoesNotExist:
            return False

    def get_activities(self):
        """TEST Returns list of activities ordered by date."""
        return self.rel_activities.order_by('-date_created')

    def add_product(self, product_id, **kw):
        """TEST Assigns products to salescycle"""
        return self.add_products([product_id], **kw)

    def add_products(self, product_ids, company_id):
        """TEST Assigns products to salescycle"""
        if isinstance(product_ids, int):
            product_ids = [product_ids]
        assert isinstance(product_ids, (tuple, list)), "must be a list"
        products = Product.objects.filter(pk__in=product_ids)
        if not products:
            return False
        for product in products:
            try:
                SalesCycleProductStat.objects.get(sales_cycle=self, product=product)
            except SalesCycleProductStat.DoesNotExist:
                s = SalesCycleProductStat(sales_cycle=self, product=product, company_id=company_id)
                s.save()

        return True

    def remove_products(self, product_ids):
        """TEST UnAssigns products to salescycle"""
        if not isinstance(product_ids, (tuple, list)):
            product_ids = [product_ids]
        products = Product.objects.filter(pk__in=product_ids)
        if not products:
            return False
        for product in products:
            try:
                s = SalesCycleProductStat.objects.get(sales_cycle=self, product=product)
                s.delete()
            except SalesCycleProductStat.DoesNotExist:
                continue
        return True

    def remove_product(self, product_id, **kw):
        """TEST Assigns products to salescycle"""
        return self.remove_products([product_id], **kw)

    def set_result(self, value_obj, save=False):
        """TEST Set salescycle.real_value to value_obj. Saves the salescycle
        if `save` is true"""
        self.real_value = value_obj
        if save:
            self.save()

    def set_result_by_amount(self, amount, company_id, succeed):
        v = Value(amount=amount, owner=self.owner)
        v.company_id = company_id
        v.save()

        if succeed:
            self.real_value = v
        else:
            self.projected_value = v
        self.save()

    def change_milestone(self, user, milestone_id, company_id):
        milestone = Milestone.objects.get(id=milestone_id)

        prev_milestone_title = None
        prev_milestone_color_code = None

        if self.milestone != None:
            prev_milestone_title = self.milestone.title
            prev_milestone_color_code = self.milestone.color_code

        self.milestone = milestone
        self.real_value = None
        self.projected_value = None
        self.save()

        for log_entry in self.log.all():
            if log_entry.entry_type == SalesCycleLogEntry.ME or \
               log_entry.entry_type == SalesCycleLogEntry.MD:
               log_entry.delete()

        meta = {
            "prev_milestone_title": prev_milestone_title,
            "prev_milestone_color_code": prev_milestone_color_code,
            "next_milestone_title": milestone.title,
            "next_milestone_color_code": milestone.color_code
        }

        sc_log_entry = SalesCycleLogEntry(meta=json.dumps(meta),
                                          entry_type=SalesCycleLogEntry.MC,
                                          sales_cycle=self,
                                          owner=user, 
                                          company_id=company_id)
        sc_log_entry.save()
        return self

    def close(self, products_with_values, company_id, succeed):
        amount = 0
        for product, value in products_with_values.iteritems():
            amount += value
            s = SalesCycleProductStat.objects.get(sales_cycle=self,
                                                  product=Product.objects.get(id=product))
            if succeed:
                s.real_value = value
            else:
                s.projected_value = value
            s.save()

        self.status = self.COMPLETED
        self.set_result_by_amount(amount, company_id, succeed)
        self.save()

        log_entry = SalesCycleLogEntry(sales_cycle=self, meta=json.dumps({"amount": amount}))
        if succeed:
            log_entry.entry_type = SalesCycleLogEntry.SC
        else:
            log_entry.entry_type = SalesCycleLogEntry.FC
        log_entry.company_id = company_id

        return [self, log_entry]

    @classmethod
    def upd_lst_activity_on_create(cls, sender,
                                   created=False, instance=None, **kwargs):
        if not created or not instance.sales_cycle.is_global:
            return
        sales_cycle = instance.sales_cycle
        sales_cycle.latest_activity = sales_cycle.find_latest_activity()
        sales_cycle.save()

    @classmethod
    def get_salescycles_by_last_activity_date(
        cls, company_id, user_id=None, owned=True, mentioned=False,
            followed=False, all=False, include_activities=False):
        """Returns sales_cycles where user is owner, mentioned or followed
            ordered by last activity date.

            Returns
            -------
            if include_activities=True:
                (Queryset<SalesCycle>,
                 Queryset<Activity>,
                 sales_cycle_activity_map =  {1: [2, 3, 4], 2:[3, 5, 7]})
            else:
                Queryset<SalesCycle>
            Raises:
                User.DoesNotExist
        """
        q0 = Q(company_id=company_id)
        q = Q()
        if not all:
            if owned:
                q |= Q(owner_id=user_id)
            if mentioned:
                q |= Q(mentions__user_id=user_id)
            if followed:
                q |= Q(followers__user_id=user_id)
        if not all and len(q.children) == 0:
            sales_cycles = SalesCycle.objects.none()
        else:
            sales_cycles = SalesCycle.objects.filter(q0 & q).order_by('-latest_activity__date_created')

        if not include_activities:
            return sales_cycles
        else:
            activities = Activity.objects.filter(
                sales_cycle_id__in=sales_cycles.values_list('pk', flat=True))
            sales_cycle_activity_map = {}
            for sc in sales_cycles:
                sales_cycle_activity_map[sc.id] = \
                    sc.rel_activities.values_list('pk', flat=True)
            return (sales_cycles, activities, sales_cycle_activity_map)

    @classmethod
    def get_salescycles_by_contact(cls, contact_id):
        """Returns queryset of sales cycles by contact"""
        return SalesCycle.objects.filter(contact_id=contact_id)

    @classmethod
    def get_salescycles_of_contact_by_last_activity_date(cls, contact_id):
        sales_cycles = cls.objects.filter(contact_id=contact_id)\
            .order_by('-latest_activity__date_created')
        return sales_cycles

    def serialize(self):
        projected_value_id = None
        real_value_id = None
        if self.projected_value:
            projected_value_id = self.projected_value.id
        if self.real_value:
            real_value_id = self.real_value.id

        return {
            'activities': [activity.id for activity in self.rel_activities.all()],
            'author_id': self.owner_id,
            'company_id': self.company_id,
            'contact_id': self.contact_id,
            'date_created': self.date_created,
            'date_edited': self.date_edited,
            'description': self.description,
            'id': self.pk,
            'is_global': self.is_global,
            'log': [l.id for l in self.log.all()],
            'milestone_id': self.milestone_id,
            'pk': self.pk,
            'product_ids': [p.id for p in self.products.all()],
            "projected_value": projected_value_id,
            "real_value": real_value_id,
            "stat": [stat.id for stat in self.product_stats.all()],
            "status": self.status,
            "title": self.title
        }

    @classmethod
    def get_by_ids(cls, *ids):
        """Get sales cycles by ids from cache with fallback to postgres."""
        rv = cache.get_many([build_key(cls._meta.model_name, sid) for sid in ids])
        rv = {extract_id(k, coerce=int): json.loads(v) for k, v in rv.iteritems()}

        not_found_ids = [cid for cid in ids if not cid in rv]
        if not not_found_ids:
            return rv.values()
        sales_cycles = cls.objects.filter(pk__in=not_found_ids).prefetch_related('rel_activities')
        more_rv = list(s.serialize() for s in sales_cycles)
        cache.set_many({build_key(cls._meta.model_name, salescycle_raw['id']): json.dumps(salescycle_raw, default=date_handler)
                        for salescycle_raw in more_rv})
        return rv.values() + more_rv

    @classmethod
    def after_save(cls, sender, instance, **kwargs):
        cache.set(build_key(cls._meta.model_name, instance.pk), json.dumps(instance.serialize(), default=date_handler))
    
    @classmethod
    def after_delete(cls, sender, instance, **kwargs):
        cache.delete(build_key(cls._meta.model_name, instance.pk))

    @classmethod
    def cache_all(cls):
        sales_cycles_qs = cls.objects.all().prefetch_related('rel_activities')
        sales_cycle_raws = [c.serialize() for c in sales_cycles_qs]
        cache.set_many({build_key(cls._meta.model_name, sales_cycle_raw['id']): json.dumps(sales_cycle_raw, default=date_handler) for sales_cycle_raw in sales_cycle_raws})

post_save.connect(SalesCycle.after_save, sender=SalesCycle)
post_delete.connect(SalesCycle.after_delete, sender=SalesCycle)

class SalesCycleLogEntry(SubscriptionObject):
    TYPES_CAPS = (
        _('Milestone change'),
        _('Milestone edited'),
        _('Milestone deleted'),
        _('Products changed'),
        _('Success close'),
        _('Fail close'),
    )
    TYPES = (MC, ME, MD, PC, SC, FC) = ('MC', 'ME', 'MD', 'PC', 'SC', 'FC')
    TYPES_OPTIONS = zip(TYPES, TYPES_CAPS)
    TYPES_DICT = dict(zip(('MC', 'ME', 'MD', 'PC', 'SC', 'FC'), TYPES))

    meta = models.TextField(null=True, blank=True)
    sales_cycle = models.ForeignKey(SalesCycle, related_name='log')
    entry_type = models.CharField(max_length=2,
                              choices=TYPES_OPTIONS, default=MC)
    owner = models.ForeignKey(User, related_name='owned_logentries', null=True)


class Activity(SubscriptionObject):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField(blank=True, null=True)
    date_finished = models.DateTimeField(blank=True, null=True)
    need_preparation = models.BooleanField(default=False, blank=True)
    sales_cycle = models.ForeignKey(SalesCycle, related_name='rel_activities')
    assignee = models.ForeignKey(User, related_name='activity_assignee', null=True)
    result = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, related_name='activity_owner', null=True)
    mentions = generic.GenericRelation('Mention', null=True)
    comments = generic.GenericRelation('Comment', null=True)
    hashtags = generic.GenericRelation('HashTagReference', null=True, blank=True)

    class Meta:
        verbose_name = 'activity'
        db_table = settings.DB_PREFIX.format('activity')

    def __unicode__(self):
        return self.description

    @property
    def author(self):
        return self.owner

    @property
    def author_id(self):
        return self.owner_id

    @author_id.setter
    def author_id(self, author_id):
        self.owner = User.objects.get(id=author_id)

    @property
    def contact(self):
        return self.sales_cycle.contact

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def new_comments_count(self):
        return len(
            filter(lambda(comment): not comment.has_read(comment.owner_id),
                   self.comments.all())
            )

    def spray(self, company_id, account):
        accounts = []
        for account in Account.objects.filter(company_id=company_id):
            if not (self.contact in account.unfollow_list.all()):
                accounts.append(account)

        with transaction.atomic():
            for account in accounts:
                act_recip = ActivityRecipient(user=account.user, activity=self)
                if account.user.id==self.owner.id:
                    act_recip.has_read = True
                act_recip.save()

    def has_read(self, user_id):
        recip = self.recipients.filter(user_id=user_id).first()
        # # OPTIMIZE VERSION =D
        # recip = None
        # for r in self.recipients.all():
        #     if r.user_id == user_id:
        #         recip = r
        #         break
        return not recip or recip.has_read

    @classmethod
    def mark_as_read(cls, user_id, act_id):
        try:
            act = ActivityRecipient.objects.get(
                user__id=user_id, activity__id=act_id)
        except ActivityRecipient.DoesNotExist:
            pass
        else:
            act.has_read = True
            act.save()
        return True

    @classmethod
    def get_filter_for_mobile(cls):
        month = (datetime.now(pytz.timezone(settings.TIME_ZONE)) - timedelta(days=7))
        return (
            Q(deadline__isnull=False, date_finished__isnull=True) |
            Q(deadline__isnull=False, date_finished__isnull=False, date_finished__gte=month) |
            Q(deadline__isnull=True,  date_edited__gte=month )
            )

    @classmethod
    def get_activities_by_contact(cls, contact_id):
        return Activity.objects.filter(sales_cycle__contact_id=contact_id)

    @classmethod
    def get_activities_by_salescycle(cls, sales_cycle_id):
        return cls.objects.filter(sales_cycle_id=sales_cycle_id).order_by('-date_created')

    @classmethod
    def get_mentioned_activities_of(cls, user_ids):
        if not user_ids is isinstance(tuple, list):
            user_ids = [user_ids]
        return Activity.objects.filter(mentions__user_id__in=user_ids)

    '''--Done--'''
    @classmethod
    def get_activity_details(
            cls, activity_id, include_sales_cycle=False,
            include_mentioned_users=False, include_comments=True):
        """TODO Returns activity details with comments by default.
        If `include_mentioned_users` is ON, then includes mentioned user.
        If `include_sales_cycle` is ON, then include its sales cycle.

        Returns
        --------
            activity - Activity object
            sales_cycle (if included)
            comments (if included)
            mentioned_users (if included)
            {'activity': {'object': ..., 'comments': [], sales_cycle: ..}}
        """
        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return False
        activity_detail = {'activity': {'object': activity}}
        if include_sales_cycle:
            activity_detail['activity'][
                'sales_cycle'] = activity.sales_cycle
        if include_mentioned_users:
            activity_detail['activity'][
                'mentioned_users'] = activity.mentions.all()
        if include_comments:
            activity_detail['activity']['comments'] = activity.comments.all()
        return activity_detail

    @classmethod
    def get_number_of_activities_by_day(cls, user_id,
                                        from_dt=None, to_dt=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False
        '''
        need to implement the conversion to datetime object
        from input arguments
        '''
        if (type(from_dt) and type(to_dt) == datetime):
            pass
        activity_queryset = Activity.objects.filter(
            date_created__gte=from_dt, date_created__lte=to_dt, owner=user)
        date_counts = {}
        for act in activity_queryset:
            date = str(act.date_created.date())
            if date in date_counts:
                date_counts[date] += 1
            else:
                date_counts[date] = 1
        return date_counts

    @classmethod
    def get_activities_by_date_created(
        cls, company_id, user_id=None, owned=True,
        mentioned=False, all=False, include_sales_cycles=False):
        """Returns activities where user is owner or mentioned
            ordered by created date.

            Returns
            -------
            if include_sales_cycles=True:
                (Queryset<Activity>,
                 Queryset<SalesCycle>,
                 sales_cycle_activity_map =  {1: [2, 3, 4], 2:[3, 5, 7]})
            else:
                Queryset<Activity>
            Raises:
                User.DoesNotExist
        """
        q0 = Q(company_id=company_id)
        q = Q()
        if not all:
            if owned:
                q |= Q(owner_id=user_id)
            if mentioned:
                q |= Q(mentions__user_id=user_id)
        if not all and len(q.children) == 0:
            activities = Activity.objects.none()
        else:
            activities = Activity.objects.filter(q & q0).order_by('-date_created')

        if not include_sales_cycles:
            return activities
        else:
            sales_cycles = SalesCycle.objects.filter(
                id__in=activities.values_list('sales_cycle_id', flat=True))
            s2a_map = {}
            for sc in sales_cycles:
                s2a_map[sc.id] = sc.rel_activities.values_list('pk', flat=True)
            return (activities, sales_cycles, s2a_map)

    def serialize(self):
        return {
            'assignee_id': self.assignee_id,            
            'author_id': self.owner_id,
            'company_id': self.company_id,
            'comments_count': self.comments_count,
            'date_created': self.date_created,
            'date_edited': self.date_edited,
            'date_finished': self.date_finished,
            'deadline': self.deadline,
            'description': self.description,
            'id': self.pk,
            'need_preparation': self.need_preparation,
            'pk': self.pk,
            'result': self.result,
            'sales_cycle_id': self.sales_cycle_id
        }

    @classmethod
    def get_by_ids(cls, *ids):
        """Get sales cycles by ids from cache with fallback to postgres."""
        rv = cache.get_many([build_key(cls._meta.model_name, aid) for aid in ids])
        rv = {extract_id(k, coerce=int): json.loads(v) for k, v in rv.iteritems()}

        not_found_ids = [aid for aid in ids if not aid in rv]
        if not not_found_ids:
            return rv.values()
        activities = cls.objects.filter(pk__in=not_found_ids)
        more_rv = list(a.serialize() for a in activities)
        cache.set_many({build_key(cls._meta.model_name, activity_raw['id']): json.dumps(activity_raw, default=date_handler)
                        for activity_raw in more_rv})
        return rv.values() + more_rv

    @classmethod
    def after_save(cls, sender, instance, **kwargs):
        cache.set(build_key(cls._meta.model_name, instance.pk), json.dumps(instance.serialize(), default=date_handler))
    
    @classmethod
    def after_delete(cls, sender, instance, **kwargs):
        cache.delete(build_key(cls._meta.model_name, instance.pk))


    @classmethod
    def cache_all(cls):
        activities = cls.objects.all()
        activity_raws = [activity.serialize() for activity in activities]
        cache.set_many({build_key(cls._meta.model_name, activity_raw['id']): json.dumps(activity_raw, default=date_handler) for activity_raw in activity_raws})

# post_save.connect(Activity.after_save, sender=Activity)
# post_delete.connect(Activity.after_delete, sender=Activity)


class ActivityRecipient(SubscriptionObject):
    activity = models.ForeignKey(Activity, related_name='recipients')
    user = models.ForeignKey(User, related_name='activities')
    has_read = models.BooleanField(default=False)

    @property
    def owner(self):
        return self.activity.owner

    class Meta:
        db_table = settings.DB_PREFIX.format('activity_recipient')

    def __unicode__(self):
        return u'Activity: %s' % self.pk or 'Unknown'


class Mention(SubscriptionObject):
    user = models.ForeignKey(User, related_name='mentions', null=True)
    owner = models.ForeignKey(User, related_name='owned_mentions', null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s %s" % (self.user, self.content_object)

    @property
    def author(self):
        return self.owner

    @classmethod
    def build_new(cls, user_id, content_class=None,
                  object_id=None, company_id = None, save=False):
        mention = cls(user_id=user_id)
        mention.content_type = ContentType.objects.get_for_model(content_class)
        mention.object_id = object_id
        mention.company_id = company_id
        if save:
            mention.save()
        return mention

    @classmethod
    def get_all_mentions_of(cls, user_id):
        """TODO Returns all mentions of user.
        Returns
        ----------
            Queryset<Mention>
        """
        return Mention.objects.filter(user_id=user_id)


class Comment(SubscriptionObject):
    comment = models.CharField(max_length=140)
    owner = models.ForeignKey(User, related_name='comment_owner', null=True)
    object_id = models.IntegerField(null=True, blank=False)
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    mentions = generic.GenericRelation('Mention')
    hashtags = generic.GenericRelation('HashTagReference', null=True, blank=True)

    def __unicode__(self):
        return "%s's comment" % (self.owner)

    @property
    def author(self):
        return self.owner

    def spray(self, company_id, account):
        accounts = []
        for account in Account.objects.filter(company_id=company_id):
            if not (self.content_object.contact in account.unfollow_list.all()):
                accounts.append(account)
                
        with transaction.atomic():
            for account in accounts:
                com_recipient = CommentRecipient(user=account.user, comment=self)
                if account.user.id==self.owner.id:
                    com_recipient.has_read = True
                com_recipient.save()

    def has_read(self, user_id):
        recip = self.recipients.filter(user_id=user_id).first()
        # # OPTIMIZE VERSION =D
        # recip = None
        # for r in self.recipients.all():
        #     if r.user_id == user_id:
        #         recip = r
        #         break
        return not recip or recip.has_read

    @classmethod
    def mark_as_read(cls, user_id, comment_id):
        try:
            comment = CommentRecipient.objects.get(
                user__id=user_id, comment__id=comment_id)
        except CommentRecipient.DoesNotExist:
            pass
        else:
            comment.has_read = True
            comment.save()
        return True

    def save(self, **kwargs):
        if self.date_created:
            self.date_edited = timezone.now()
        super(Comment, self).save(**kwargs)

    def add_mention(self, user_ids=None):
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        build_single_mention = functools.partial(Mention.build_new,
                                                 content_class=self.__class__,
                                                 object_id=self.pk,
                                                 save=True)
        self.mentions = map(build_single_mention, user_ids)
        self.save()

    @classmethod
    def build_new(cls, user_id, content_class=None,
                  object_id=None, save=False):
        comment = cls(owner_id=user_id)
        comment.content_type = ContentType.objects.get_for_model(content_class)
        comment.object_id = object_id
        if save:
            comment.save()
        return comment

    '''---done---'''
    @classmethod
    def get_comments_by_context(cls, context_object_id, context_class):
        try:
            cttype = ContentType.objects.get_for_model(context_class)
        except ContentType.DoesNotExist:
            return False
        return cls.objects.filter(
            object_id=context_object_id,
            content_type=cttype)



class CommentRecipient(SubscriptionObject):
    comment = models.ForeignKey(Comment, related_name='recipients')
    user = models.ForeignKey(User, related_name='comments')
    has_read = models.BooleanField(default=False)

    @property
    def owner(self):
        return self.comment.owner

    class Meta:
        db_table = settings.DB_PREFIX.format('comment_recipient')

    def __unicode__(self):
        return u'Comment: %s' % self.pk or 'Unknown'


class Share(SubscriptionObject):
    is_read = models.BooleanField(default=False, blank=False)
    contact = models.ForeignKey(Contact, related_name='share_set', blank=True, null=True)
    share_to = models.ForeignKey(User, related_name='in_shares', null=True)
    share_from = models.ForeignKey(User, related_name='owned_shares', null=True)
    comments = generic.GenericRelation('Comment')
    note = models.CharField(max_length=500, null=True)
    hashtags = generic.GenericRelation('HashTagReference', null=True, blank=True)
    mentions = generic.GenericRelation('Mention')

    class Meta:
        verbose_name = 'share'
        db_table = settings.DB_PREFIX.format('share')

    @property
    def owner(self):
        return self.share_from

    @owner.setter
    def owner(self, owner_object):
        self.share_from = owner_object

    @classmethod
    def get_shares(cls, company_id):
        q = Q(company_id=company_id)
        return cls.objects.filter(q).order_by('-date_created')

    @classmethod
    def get_shares_in_for(cls, user_id):
        return cls.objects.filter(share_to__pk=user_id)\
            .order_by('-date_created')

    def __unicode__(self):
        return u'%s : %s -> %s' % (self.contact, self.share_from, self.share_to)



signals.post_save.connect(
    Contact.upd_lst_activity_on_create, sender=Activity)
signals.post_save.connect(
    Contact.upd_status_when_first_activity_created, sender=Activity)
signals.post_save.connect(
    SalesCycle.upd_lst_activity_on_create, sender=Activity)


def on_activity_delete(sender, instance=None, **kwargs):
    sales_cycle = instance.sales_cycle
    act = sales_cycle.find_latest_activity()
    # todo(xepa4ep): this should imply rather then patch
    try:
        sales_cycle.latest_activity = sales_cycle.find_latest_activity()
    except Activity.DoesNotExist:
        wrong_cycles = SalesCycle.objects.filter(latest_activity=act)
        for cycle in wrong_cycles:
            cycle.latest_activity = cycle.find_latest_activity()
            cycle.save()
    sales_cycle.save()

    contact = sales_cycle.contact
    contact.latest_activity = contact.find_latest_activity()
    contact.save()

def check_is_title_empty(sender, instance=None, **kwargs):
    if len(instance.title) == 0:
        raise Exception("Requires non empty value")

def create_milestones(sender, instance, **kwargs):
    if Milestone.objects.filter(company_id=instance.id).count() == 0:
        milestones = Milestone.create_default_milestones(instance.id)

def delete_related_milestones(sender, instance, **kwargs):
    for milestone in Milestone.objects.filter(company_id=instance.id):
        milestone.delete()

signals.post_delete.connect(on_activity_delete, sender=Activity)
signals.pre_save.connect(check_is_title_empty, sender=SalesCycle)
signals.post_save.connect(create_milestones, sender=Company)
signals.pre_delete.connect(delete_related_milestones, sender=Company)

'''
Function to get mentions by 3 of optional parameters:
either for a particular user or for all users
'''


def get_mentions(user_id=None, content_class=None, object_id=None):
    cttype = ContentType.objects.get_for_model(content_class)
    return Mention.objects.filter(user_id=user_id,
                                  content_type=cttype,
                                  object_id=object_id)


class ContactList(SubscriptionObject):
    owner = models.ForeignKey(User, related_name='owned_list', blank=True, null=True)
    title = models.CharField(max_length=150)
    contacts = models.ManyToManyField(Contact, related_name='contact_list',
                                   null=True, blank=True)
    import_task = models.OneToOneField('alm_crm.ImportTask', 
        blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('contact_list')
        db_table = settings.DB_PREFIX.format('contact_list')

    def __unicode__(self):
        return self.title

    @classmethod
    def get_for_subscr(cls, company_id):
        return cls.objects.filter(company_id=company_id)

    def check_contact(self, contact_id):
        try:
            contact = self.contacts.get(id=contact_id)
            if contact is not None:
                return True
            else:
                return False
        except Contact.DoesNotExist:
            return False

    def get_contacts(self):
        return self.contacts

    def add_contacts(self, contact_ids):
        assert isinstance(contact_ids, (tuple, list)), 'must be a list'
        status = []
        for contact_id in contact_ids:
            try:
                contact = Contact.objects.get(id=contact_id)
                if not self.check_contact(contact_id=contact_id):
                    self.contacts.add(contact)
                    status.append(True)
                else:
                    status.append(False)
            except Contact.DoesNotExist:
                status.append(False)
        return status

    def add_contact(self, contact_id):
        return self.add_contacts([contact_id])

    def delete_contact(self, contact_id):
        status = False
        if self.check_contact(contact_id):
            contact = Contact.objects.get(id=contact_id)
            try:
                self.contacts.remove(contact)
                status = True
            except Contact.DoesNotExist:
                status = False
        else:
            return False

        return status

    def count(self):
        return self.contacts.count()


class SalesCycleProductStat(SubscriptionObject):
    sales_cycle = models.ForeignKey(SalesCycle, related_name='product_stats',
                                null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product)
    real_value = models.IntegerField(default=0)
    projected_value = models.IntegerField(default=0)

    @property
    def owner(self):
        return self.sales_cycle.owner

    class Meta:
        verbose_name = _('sales_cycle_product_stat')
        db_table = settings.DB_PREFIX.format('cycle_prod_stat')

    def __unicode__(self):
        return u'%s | %s | %s' % (self.sales_cycle, self.product, self.real_value)


class Filter(SubscriptionObject):
    BASE_OPTIONS = (
        ('AL', _('all')),
        ('RT', _('recent')),
        ('CD', _('cold')),
        ('LD', _('lead')))
    title = models.CharField(max_length=100, default='')
    filter_text = models.CharField(max_length=500)
    owner = models.ForeignKey(User, related_name='owned_filter', null=True)
    
    base = models.CharField(max_length=6, choices=BASE_OPTIONS, default='all')

    class Meta:
        verbose_name = _('filter')
        db_table = settings.DB_PREFIX.format('filter')

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.base)

    def save(self, **kwargs):
        if not self.company_id and self.owner:
            self.company_id = self.owner.company_id
        super(self.__class__, self).save(**kwargs)


class HashTag(SubscriptionObject):
    text = models.CharField(max_length=500)

    class Meta:
        verbose_name = _('hashtag')
        db_table = settings.DB_PREFIX.format('hashtag')
        unique_together = ('company_id', 'text')

    def __unicode__(self):
        return u'%s' % (self.text)


class HashTagReference(SubscriptionObject):
    hashtag = models.ForeignKey(HashTag, related_name="references")
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @property
    def owner(self):
        return content_object.owner

    class Meta:
        verbose_name = _('hashtag_reference')
        db_table = settings.DB_PREFIX.format('hashtag_reference')

    def __unicode__(self):
        return u'%s' % (self.hashtag)

    @classmethod
    def build_new(cls, hashtag_id, content_class=None,
                  object_id=None, company_id=None, save=False):
        hashtag_reference = cls(hashtag_id=hashtag_id)
        hashtag_reference.content_type = ContentType.objects.get_for_model(content_class)
        hashtag_reference.object_id = object_id
        hashtag_reference.company_id = company_id
        if save:
            hashtag_reference.save()
        return hashtag_reference


class CustomSection(SubscriptionObject):
    title = models.CharField(max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @property
    def owner(self):
        if self.content_object.__class__ == VCard:
            return self.content_object.contact.owner
        return self.content_object.owner

    class Meta:
        verbose_name = _('custom_section')
        db_table = settings.DB_PREFIX.format('custom_sections')

    def __unicode__(self):
        return u'%s' % self.title

    @classmethod
    def build_new(cls, title=None, content_class=None,
                  object_id=None, save=False):
        custom_field = cls(title=title)
        custom_field.content_type = ContentType.objects.get_for_model(content_class)
        custom_field.object_id = object_id
        if save:
            custom_field.save()
        return custom_field


class CustomField(SubscriptionObject):
    title = models.CharField(max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)

    class Meta:
        verbose_name = _('custom_field')
        db_table = settings.DB_PREFIX.format('custom_fields')

    def __unicode__(self):
        return u'%s' % (self.title)

    @classmethod
    def after_save_delete(cls, sender, instance, **kwargs):
        if instance.content_type.model_class()==Contact:
            custom_field_values = CustomFieldValue.objects.filter(custom_field=instance)
            contact_ids = [c.content_object.id for c in custom_field_values]
            Contact.recache(contact_ids)

    @classmethod
    def build_new(cls, title=None, content_class=None, save=False):
        custom_field = cls(title=title)
        if content_class:
            custom_field.content_type = ContentType.objects.get_for_model(content_class)
        if save:
            custom_field.save()
        return custom_field

signals.post_save.connect(CustomField.after_save_delete, sender=CustomField)
signals.post_delete.connect(CustomField.after_save_delete, sender=CustomField)

class CustomFieldValue(SubscriptionObject):
    custom_field = models.ForeignKey('CustomField', related_name="values")
    value = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @property
    def owner(self):
        return self.content_object.owner

    class Meta:
        verbose_name = _('custom_field_value')
        db_table = settings.DB_PREFIX.format('custom_field_values')

    def __unicode__(self):
        return u'%s: %s' % (self.custom_field.title, self.value)

    @classmethod
    def after_save_delete(cls, sender, instance, **kwargs):
        if isinstance(instance.content_object, Contact):
            Contact.recache([instance.content_object.id])


    @classmethod
    def build_new(cls, field, value=None, object_id=None, save=False):
        custom_field_val = cls(custom_field=field, value=value)
        if object_id:
            custom_field_val.content_type = field.content_type
            custom_field_val.object_id = object_id
        if save:
            custom_field_val.save()
        return custom_field_val

signals.post_save.connect(CustomFieldValue.after_save_delete, sender=CustomFieldValue)
signals.post_delete.connect(CustomFieldValue.after_save_delete, sender=CustomFieldValue)

class ImportTask(models.Model):
    uuid = models.CharField(blank=True, null=True, max_length=100)
    finished = models.BooleanField(default=False)
    filename = models.CharField(max_length=250)
    imported_num = models.IntegerField(default=0, blank=True, null=True)
    not_imported_num = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        if not self.uuid:
            return str(self.finished)
        return self.uuid + ' ' + str(self.finished)


class ErrorCell(models.Model):
    import_task = models.ForeignKey(ImportTask)
    row = models.IntegerField()
    col = models.IntegerField()
    data = models.CharField(max_length=10000)
