# -*- coding: utf-8 -*-

import os
import xlrd
import pytz
import simplejson as json
import dateutil.parser
from datetime import datetime, timedelta, time
from celery import group, Task, result

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.db.models import signals, Q
from django.db import models, transaction, IntegrityError
from django.conf import settings

from almanet.utils.metaprogramming import DirtyFieldsMixin
from almanet.utils.cache import build_key, extract_id
from almanet.utils.json import date_handler
from almanet.models import SubscriptionObject, Subscription
from alm_company.models import Company
from alm_user.models import User, Account
from alm_vcard import models as vcard_models
from alm_vcard.models import (
    VCard,
    BadVCardError,
    Title,
    Tel,
    Email,
    Category,
    Adr,
    Url,
    Note,
    )
from .utils import datetimeutils
import re
HASHTAG_PARSER = re.compile(u'\B#\w*[а-яА-ЯёЁa-zA-Z]+\w*', re.U)

TEMP_DIR = getattr(settings, 'TEMP_DIR')
ALLOWED_TIME_PERIODS = ['week', 'month', 'year']
CURRENCY_OPTIONS = (
    ('USD', 'US Dollar'),
    ('RUB', 'Rubbles'),
    ('KZT', 'Tenge'),
)
GLOBAL_CYCLE_TITLE = _('Main flow')
GLOBAL_CYCLE_DESCRIPTION = _('Automatically generated cycle')

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
        """
            'Звонок/Заявка'
            'Отправка КП'
            'Согласование договора'
            'Выставление счета'
            'Контроль оплаты'
            'Предоставление услуги'
            'Upsales'
            'Успешно завершено'
            'Не реализовано'
        """
        milestones = []
        default_data = [{'title':_('Call/request'), 'color_code': '#F4B59C', 'is_system':0, 'sort':1},
                        {'title':_('Dispatching business offer'), 'color_code': '#F59CC8', 'is_system':0, 'sort':2},
                        {'title':_('Negotiating contract'), 'color_code': '#A39CF4', 'is_system':0, 'sort':3},
                        {'title':_('Invoicing'), 'color_code': '#9CE5F4', 'is_system':0, 'sort':4},
                        {'title':_('Payment control'), 'color_code': '#9CF4A7', 'is_system':0, 'sort':5},
                        {'title':_('Service provision'), 'color_code': '#D4F49B', 'is_system':0, 'sort':6},
                        {'title':_('Successful'), 'color_code':'#9CF4A7', 'is_system':1, 'sort':7},
                        {'title':_('Failed'), 'color_code':'#F4A09C', 'is_system':2, 'sort':8}]

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
        'Contact', blank=True, null=True, 
        related_name='children', on_delete=models.SET_NULL)
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


    @property
    def last_contacted(self):
        return self.latest_activity and self.latest_activity.date_created

    @property
    def global_sales_cycle(self):
        return SalesCycle.objects.get(company_id=self.company_id, contact_id=self.id,
                                      is_global=True)

    @property
    def name(self):
        if not self.vcard:
            return _('Unknown')
        return self.vcard.fn

    @classmethod
    def get_panel_info(cls, company_id, user_id):
        contacts_q = Q(company_id=company_id)
        owner_q = Q(owner_id=user_id)

        period_q = {
            'days_q': Q(date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), date_edited__lte=datetimeutils.get_end_of_today(timezone.now())),
            'weeks_q': Q(date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), date_edited__lte=datetimeutils.get_end_of_week(timezone.now())),
            'months_q': Q(date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), date_edited__lte=datetimeutils.get_end_of_month(timezone.now())),
        }

        total = Contact.objects.filter(contacts_q)
        my_total = total.filter(owner_q)

        periods = ['days', 'weeks', 'months']

        def get_by_period(queryset):
            rv = {}
            for period in periods:
                period_total = queryset.filter(period_q[period+'_q'])
                rv[period] = period_total.count()
            return rv

        return {
                'all': {
                    'total': total.count(),
                    'people': total.filter(Q(tp=Contact.USER_TP)).count(),
                    'companies': total.filter(Q(tp=Contact.COMPANY_TP)).count(),
                    'by_period': get_by_period(total),
                },
                'my': {
                    'total': my_total.count(),
                    'people': my_total.filter(Q(tp=Contact.USER_TP)).count(),
                    'companies': my_total.filter(Q(tp=Contact.COMPANY_TP)).count(),
                    'by_period': get_by_period(my_total),
                },
            }

    @classmethod
    def get_active_contacts(cls, company_id, user_id):
        company_q = Q(company_id=company_id)
        owner_q = Q(owner_id=user_id)

        days_q = Q(date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), date_edited__lte=datetimeutils.get_end_of_today(timezone.now()))
        weeks_q = Q(date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), date_edited__lte=datetimeutils.get_end_of_week(timezone.now()))
        months_q = Q(date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), date_edited__lte=datetimeutils.get_end_of_month(timezone.now()))

        latest_activity_days_q = Q(latest_activity__date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), latest_activity__date_edited__lte=datetimeutils.get_end_of_today(timezone.now()))
        latest_activity_weeks_q = Q(latest_activity__date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), latest_activity__date_edited__lte=datetimeutils.get_end_of_week(timezone.now()))
        latest_activity_months_q = Q(latest_activity__date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), latest_activity__date_edited__lte=datetimeutils.get_end_of_month(timezone.now()))

        return {
            'all': {
                'days': Contact.objects.filter(company_q & (days_q | latest_activity_days_q)),
                'weeks': Contact.objects.filter(company_q & (days_q | latest_activity_weeks_q)),
                'months': Contact.objects.filter(company_q & (days_q | latest_activity_months_q)),
            },
            'my': {
                'days': Contact.objects.filter((company_q & owner_q) & (days_q | latest_activity_days_q)),
                'weeks': Contact.objects.filter((company_q & owner_q) & (weeks_q | latest_activity_days_q)),
                'months': Contact.objects.filter((company_q & owner_q) & (months_q | latest_activity_days_q)),
            },
        }

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

    @classmethod
    def upd_lst_activity_on_create(cls, sender, created=False,
                                   instance=None, **kwargs):
        if not created or instance.sales_cycle.is_global:
            return
        c = instance.sales_cycle.contact
        c.latest_activity = instance
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
                    # org = Org(vcard=v)
                    # org.organization_name = data[i][5].decode('utf-8')
                    # org.save()
                    pass
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
        vcard = VCard(fn=_('No name'))
        vcard.save()
        response = {}
        for structure_dict in file_structure:
            company_name = ""
            col_num = int(structure_dict.get('num'))
            if structure_dict.get('model') == 'Org':
                model = 'Org'
            else:
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
            elif model == 'Org':
                try:
                    if data[col_num].value:
                        objects = data[col_num].value.split(';')
                        for object in objects:
                            v_type = structure_dict.get('attr','')
                            company_name = object
                            # obj = model(organization_name = object)
                            # obj.vcard = vcard
                            # obj.save()
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
        if vcard.fn == 'Без Имени' and company_name:
            vcard.fn = company_name
            vcard.save()
            contact.tp = 'co'
        elif vcard.fn == 'Без Имени' and vcard.emails.first():
            vcard.fn = vcard.emails.first().value
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
        try:
            if contact.vcard.fn != company_name:
                company = Contact.objects.filter(
                    tp='co',
                    company_id=contact.company_id,
                    vcard__fn=company_name
                    ).first()
                if company:
                    contact.parent = company
                    contact.save()
                else:
                    company = contact.create_company_for_contact(company_name)
                    company.import_task = import_task
                    company.save()
                    SalesCycle.create_globalcycle(
                            **{'company_id':company.company_id,
                             'owner_id':creator.id,
                             'contact_id':company.id
                            }
                        )
        except:
            pass
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
    def delete_contacts(cls, obj_ids):
        if isinstance(obj_ids, int):
            obj_ids = [obj_ids]
        assert isinstance(obj_ids, (tuple, list)), "must be a list"
        with transaction.atomic():
            objects = {
                "contacts": [],
                "parent_dict": {},
                "children_dict": {},
                "sales_cycles": [],
                "activities": [],
                "shares": [],
                "does_not_exist": []
            }
            for contact_id in obj_ids:
                try:
                    # print contact_id
                    obj = Contact.objects.get(id=contact_id)
                    if obj.parent:
                        objects['parent_dict'][obj.id]=obj.parent.id
                    if obj.children:
                        objects['children_dict'][obj.id] = [child.id for child in obj.children.all()]
                    objects['contacts'].append(contact_id)
                    objects['sales_cycles'] += list(obj.sales_cycles.all().values_list("id", flat=True))
                    for sales_cycle in obj.sales_cycles.all():
                        objects['activities'] += list(sales_cycle.rel_activities.all().values_list("id", flat=True))
                    objects['shares'] += list(obj.share_set.all().values_list("id", flat=True))
                    obj.delete()
                except ObjectDoesNotExist:
                    objects['does_not_exist'].append(contact_id)
            return objects

    @classmethod
    def get_statistics(cls, company_id, user_id):
        shared = Share.get_by_user(company_id=company_id, user_id=user_id)

        return {
            'shared': {
                'count': shared['shares'].count(),
                'not_read': shared['not_read'],
            },
            'all': cls.get_all(company_id=company_id).count(),
            'coldbase': cls.get_cold_base(company_id=company_id, user_id=user_id).count(),
            'leadbase': cls.get_lead_base(company_id=company_id, user_id=user_id).count(),
            'recentbase': cls.get_recent_base(company_id=company_id, user_id=user_id).count(),
        }

    @classmethod
    def get_lead_base(cls, company_id, user_id):
        return  Contact.objects.filter(company_id=company_id, id__in= \
                    SalesCycle.objects.filter(company_id=company_id, id__in= \
                        Activity.objects.filter(company_id=company_id, owner_id=user_id).values_list('sales_cycle_id', flat=True) \
                    ).values_list('contact_id', flat=True) \
                ).order_by('vcard__fn')

    @classmethod
    def get_cold_base(cls, company_id, user_id):
        return  Contact.objects.filter(company_id=company_id).exclude(id__in= \
                    SalesCycle.objects.filter(company_id=company_id, id__in= \
                        Activity.objects.filter(company_id=company_id, owner_id=user_id).values_list('sales_cycle_id', flat=True) \
                    ).values_list('contact_id', flat=True) \
                ).order_by('vcard__fn')

    @classmethod
    def get_all(cls, company_id, user_id=None):
        queryset = Contact.objects.filter(
            company_id=company_id).order_by('vcard__fn')
        return queryset

    @classmethod
    def get_recent_base(cls, company_id, user_id):
        return  Contact.objects.filter(company_id=company_id, \
                                       latest_activity__owner_id=user_id, \
                                       latest_activity__date_edited=timezone.now() - timedelta(days=7)) \
                               .order_by('-latest_activity__date_edited')

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

    def delete(self):
        if self.vcard:
            self.vcard.delete()
        super(self.__class__, self).delete()

    def find_latest_activity(self):
        """Find latest activity among all sales_cycle_contacts."""
        sales_cycle = self.sales_cycles.order_by('latest_activity__date_created').first()
        latest_activity = None
        try:
            latest_activity = sales_cycle.latest_activity
        except Activity.DoesNotExist:
            return None
        return sales_cycle and latest_activity or None

    def create_company_for_contact(self, company_name):
        with transaction.atomic():
            parent = Contact.objects.filter(
                        vcard__fn=company_name, 
                        company_id=self.company_id, 
                        tp='co').first()
            if not parent:
                vcard = VCard(fn=company_name)
                vcard.save()
                parent = Contact(
                    tp='co',
                    vcard=vcard,
                    owner=self.owner,
                    company_id=self.company_id
                )
                parent.save()
                SalesCycle.create_globalcycle(
                    **{
                     'company_id': self.company_id,
                     'owner_id': self.owner.id,
                     'contact_id': parent.id
                    }
                )

            self.parent = parent
            self.save()
            return self, parent

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

    def merge_contacts(self, alias_objects=[], delete_merged=True):
        if not alias_objects:
            return {'success':False, 'message':'No alias objects appended'}
        for obj in alias_objects:
            if not isinstance(obj, self.__class__):
                return {'success':False, 'message':'Not Instance of Contact'}

        global_sales_cycle = SalesCycle.get_global(self.company_id, self.id)
        fn_list = []
        for obj in alias_objects:
            if type(obj.vcard.fn)==unicode:
                fn_list.append(obj.vcard.fn.encode('utf-8'))
            else:
                fn_list.append(obj.vcard.fn)
        try:
            note_data = self.vcard.notes.last().data if type(self.vcard.notes.last().data)==unicode else self.vcard.notes.last().data.encode('utf-8')
        except:
            note_data = ""
        for obj in alias_objects:
            if obj.vcard.notes.all():
                if type(obj.vcard.notes.last().data)==unicode:
                    note_data += "\n" + obj.vcard.notes.last().data.encode('utf-8')
                else:
                    note_data += "\n" + obj.vcard.notes.last().data
        with transaction.atomic():
            for obj in alias_objects:
                for sales_cycle in obj.sales_cycles.all():
                    if sales_cycle.is_global:
                        for activity in sales_cycle.rel_activities.all():
                            activity.sales_cycle = global_sales_cycle
                            activity.save()
                    else:
                        sales_cycle.contact = self
                        sales_cycle.save()
                if obj.children.all():
                    for child in obj.children.all():
                        self.children.add(child)

        VCard.merge_model_objects(self.vcard, [c.vcard for c in alias_objects])
        self.vcard.notes.all().delete()
        if note_data or fn_list:
            note = Note(
                data=', '.join(map(str,fn_list)) + ' ' + note_data, 
                vcard=self.vcard)
            note.save()
        with transaction.atomic():
            for obj in alias_objects:
                for share in obj.share_set.all():
                    share.contact = self
                    share.save()
        return self

    def get_products(self):
        return Product.objects.filter(id__in= \
            self.sales_cycles.all().values_list('products', flat=True).distinct())

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
            'parent_id': self.parent_id,
            # 'children': [child.pk for child in self.children.all()],
            'sales_cycles': [cycle.pk for cycle in self.sales_cycles.all()],
            'status': self.status,
            'tp': self.tp,
            'vcard_id': self.vcard_id
        }

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

    owner = models.ForeignKey(User, null=True, blank=True,
        related_name='owned_values')

    class Meta:
        verbose_name = 'value'
        db_table = settings.DB_PREFIX.format('value')

    def __unicode__(self):
        return "%s %s %s" % (self.amount, self.currency, self.salary)


class Product(SubscriptionObject):
    name = models.CharField(_('product name'), max_length=100, blank=False)
    description = models.TextField(_('product description'), blank=True, null=True)
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS,
                                default='KZT')
    custom_field_values = generic.GenericRelation('CustomFieldValue')
    owner = models.ForeignKey(User, null=True, blank=True,
        related_name='crm_products')

    class Meta:
        verbose_name = _('product')
        db_table = settings.DB_PREFIX.format('product')

    def __unicode__(self):
        return self.name

    @property
    def stat_value(self):
        return reduce(lambda x, y: x+y.real_value, self.product_stats.all(), 0)

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
        _('Successful'),
        _('Failed'))
    STATUSES = (NEW, PENDING, SUCCESSFUL, FAILED) = ('N', 'P', 'S', 'F')
    STATUSES_OPTIONS = zip(STATUSES, STATUSES_CAPS)
    STATUSES_DICT = dict(zip(('NEW', 'PENDING', 'SUCCESSFUL', 'FAILED'), STATUSES))

    is_global = models.BooleanField(default=False)

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
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

    @property
    def activities_count(self):
        return self.rel_activities.count()

    @classmethod
    def get_global(cls, company_id, contact_id):
        return SalesCycle.objects.get(company_id=company_id, contact_id=contact_id,
                                      is_global=True)

    @classmethod
    def get_statistics(cls, company_id, user_id):
        return {
            'all_sales_cycles': SalesCycle.get_all(company_id=company_id).count(),
            'new_sales_cycles': SalesCycle.get_new_all(company_id=company_id).count(),
            'successful_sales_cycles': SalesCycle.get_successful_all(company_id=company_id).count(),
            'failed_sales_cycles': SalesCycle.get_failed_all(company_id=company_id).count(),
            'open_sales_cycles': SalesCycle.get_pending_all(company_id=company_id).count(),
            'my_sales_cycles': SalesCycle.get_my(company_id=company_id, user_id=user_id).count(),
            'my_new_sales_cycles': SalesCycle.get_new_my(company_id=company_id, user_id=user_id).count(),
            'my_successful_sales_cycles': SalesCycle.get_successful_my(company_id=company_id, user_id=user_id).count(),
            'my_failed_sales_cycles': SalesCycle.get_failed_my(company_id=company_id, user_id=user_id).count(),
            'my_open_sales_cycles': SalesCycle.get_pending_my(company_id=company_id, user_id=user_id).count(),
        }

    @classmethod
    def get_all(cls, company_id):
        sales_cycle_q = Q(company_id=company_id, is_global=False)
        total = SalesCycle.objects.filter(sales_cycle_q)

        return total

    @classmethod
    def get_new_all(cls, company_id):
        sales_cycle_q = Q(company_id=company_id, is_global=False)
        total = SalesCycle.objects.filter(sales_cycle_q)

        return total.filter(status=SalesCycle.NEW)

    @classmethod
    def get_pending_all(cls, company_id):
        sales_cycle_q = Q(company_id=company_id, is_global=False)
        total = SalesCycle.objects.filter(sales_cycle_q)

        return total.filter(status=SalesCycle.PENDING)

    @classmethod
    def get_successful_all(cls, company_id):
        sales_cycle_q = Q(company_id=company_id, is_global=False)
        total = SalesCycle.objects.filter(sales_cycle_q)

        return total.filter(status=SalesCycle.SUCCESSFUL)

    @classmethod
    def get_failed_all(cls, company_id):
        sales_cycle_q = Q(company_id=company_id, is_global=False)
        total = SalesCycle.objects.filter(sales_cycle_q)

        return total.filter(status=SalesCycle.FAILED)

    @classmethod
    def get_my(cls, company_id, user_id):
        owner_q = Q(owner_id=user_id)

        return SalesCycle.get_all(company_id=company_id).filter(owner_q)

    @classmethod
    def get_new_my(cls, company_id, user_id):
        owner_q = Q(owner_id=user_id)

        return SalesCycle.get_new_all(company_id=company_id).filter(owner_q)

    @classmethod
    def get_pending_my(cls, company_id, user_id):
        owner_q = Q(owner_id=user_id)

        return SalesCycle.get_pending_all(company_id=company_id).filter(owner_q)

    @classmethod
    def get_successful_my(cls, company_id, user_id):
        owner_q = Q(owner_id=user_id)

        return SalesCycle.get_successful_all(company_id=company_id).filter(owner_q)

    @classmethod
    def get_failed_my(cls, company_id, user_id):
        owner_q = Q(owner_id=user_id)

        return SalesCycle.get_failed_all(company_id=company_id).filter(owner_q)

    @classmethod
    def get_panel_info(cls, company_id, user_id):
        period_q = {
            'days_q': Q(date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), date_edited__lte=datetimeutils.get_end_of_today(timezone.now())),
            'weeks_q': Q(date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), date_edited__lte=datetimeutils.get_end_of_week(timezone.now())),
            'months_q': Q(date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), date_edited__lte=datetimeutils.get_end_of_month(timezone.now())),
        }

        periods = ['days', 'weeks', 'months']

        new_sales_cycles =  SalesCycle.get_new_all(company_id=company_id)
        successful_sales_cycles =  SalesCycle.get_successful_all(company_id=company_id)
        open_sales_cycles =  SalesCycle.get_pending_all(company_id=company_id)
        
        my_new_sales_cycles =  SalesCycle.get_new_my(company_id=company_id, user_id=user_id)
        my_successful_sales_cycles =  SalesCycle.get_successful_my(company_id=company_id, user_id=user_id)
        my_open_sales_cycles =  SalesCycle.get_pending_my(company_id=company_id, user_id=user_id)

        milestones = Milestone.objects.filter(company_id=company_id)

        by_milestones = {
            'none': open_sales_cycles.filter(Q(milestone_id=None)).distinct().count(),
        }
        my_by_milestones = {
            'none': my_open_sales_cycles.filter(Q(milestone_id=None)).distinct().count(),
        }

        for m in milestones:
            by_milestones[m.id] = open_sales_cycles.filter(Q(milestone_id=m.id)).distinct().count()
            my_by_milestones[m.id] = my_open_sales_cycles.filter(Q(milestone_id=m.id)).distinct().count()

        def get_by_period(queryset):
            rv = {}
            for period in periods:
                period_total = queryset.filter(period_q[period+'_q'])
                rv[period] = period_total.distinct().count()
            return rv

        return {
            'new_sales_cycles': {
                'all': {
                    'total': new_sales_cycles.count(),
                    'by_period': get_by_period(new_sales_cycles),
                },
                'my': {
                    'total': my_new_sales_cycles.count(),
                    'by_period': get_by_period(my_new_sales_cycles),
                },
            },
            'successful_sales_cycles': {
                'all': {
                    'total': successful_sales_cycles.count(),
                    'by_period': get_by_period(successful_sales_cycles),
                },
                'my': {
                    'total': my_successful_sales_cycles.count(),
                    'by_period': get_by_period(my_successful_sales_cycles),
                },
            },
            'open_sales_cycles': {
                'all': {
                    'total': open_sales_cycles.count(),
                    'by_milestones': by_milestones,
                    'by_period': get_by_period(open_sales_cycles),
                },
                'my': {
                    'total': my_open_sales_cycles.count(),
                    'by_milestones': my_by_milestones,
                    'by_period': get_by_period(my_open_sales_cycles),
                },
            },
        }

    @classmethod
    def get_active_deals(cls, company_id, user_id):
        company_q = Q(company_id=company_id)
        owner_q = Q(owner_id=user_id)

        days_q = Q(date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), date_edited__lte=datetimeutils.get_end_of_today(timezone.now()))
        weeks_q = Q(date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), date_edited__lte=datetimeutils.get_end_of_week(timezone.now()))
        months_q = Q(date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), date_edited__lte=datetimeutils.get_end_of_month(timezone.now()))

        latest_activity_days_q = Q(latest_activity__date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), latest_activity__date_edited__lte=datetimeutils.get_end_of_today(timezone.now()))
        latest_activity_weeks_q = Q(latest_activity__date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), latest_activity__date_edited__lte=datetimeutils.get_end_of_week(timezone.now()))
        latest_activity_months_q = Q(latest_activity__date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), latest_activity__date_edited__lte=datetimeutils.get_end_of_month(timezone.now()))

        return {
            'all': {
                'days': SalesCycle.objects.filter(company_q & (days_q | latest_activity_days_q)),
                'weeks': SalesCycle.objects.filter(company_q & (days_q | latest_activity_weeks_q)),
                'months': SalesCycle.objects.filter(company_q & (days_q | latest_activity_months_q)),
            },
            'my': {
                'days': SalesCycle.objects.filter((company_q & owner_q) & (days_q | latest_activity_days_q)),
                'weeks': SalesCycle.objects.filter((company_q & owner_q) & (weeks_q | latest_activity_days_q)),
                'months': SalesCycle.objects.filter((company_q & owner_q) & (months_q | latest_activity_days_q)),
            },
        }

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

    @classmethod
    def upd_lst_activity_on_create(cls, sender,
                                   created=False, instance=None, **kwargs):
        if not created or instance.sales_cycle.is_global:
            return
        sales_cycle = instance.sales_cycle
        sales_cycle.latest_activity = instance
        sales_cycle.save()

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

    def possibly_make_new(self):
        if self.rel_activities.count() == 0 and self.milestone is None:
            self.status = SalesCycle.NEW
            self.save()

    def possibly_make_pending(self):
        if self.rel_activities.count() != 0 or (self.milestone is not None and self.milestone.is_system == 0):
            self.status = SalesCycle.PENDING
            self.save()

    def possibly_make_successful(self):
        if self.milestone is not None and self.milestone.is_system == 1:
            self.status = SalesCycle.SUCCESSFUL
            self.save()

    def possibly_make_failed(self):
        if self.milestone is not None and self.milestone.is_system == 2:
            self.status = SalesCycle.FAILED
            self.save()

    def find_latest_activity(self):
        return self.rel_activities.order_by('-date_created').first()

    def change_products(self, product_ids, user_id, company_id):
        old_product_ids = self.products.all().values_list('id', flat=True)

        added = Product.objects.filter(id__in=list(set(product_ids) - set(old_product_ids))).values_list('name', flat=True)
        deleted = Product.objects.filter(id__in=list(set(old_product_ids) - set(product_ids))).values_list('name', flat=True)
        total_products = []

        self.products.clear()
        products = Product.objects.filter(pk__in=product_ids)
        
        for product in products:
            try:
                SalesCycleProductStat.objects.get(sales_cycle=self, product=product)
            except SalesCycleProductStat.DoesNotExist:
                s = SalesCycleProductStat(sales_cycle=self, product=product, company_id=company_id)
                s.save()
                total_products.append({
                    'id': product.id,
                    'name': product.name
                })

        meta = {"added": list(added),
                "deleted": list(deleted),
                "products": total_products}
        log_entry = SalesCycleLogEntry(sales_cycle=self,
                                        owner_id=user_id,
                                        company_id=company_id,
                                        entry_type=SalesCycleLogEntry.PC,
                                        meta=json.dumps(meta))
        log_entry.save()

        return self

    def set_result_by_amount(self, amount, user_id, company_id, succeed):
        v = Value(
            amount=amount, 
            owner_id=user_id,
            company_id=company_id
        )
        v.save()

        if succeed:
            self.real_value = v
        else:
            self.projected_value = v
        self.save()

    def change_milestone(self, milestone_id, user_id, company_id):
        """
        If no milestone is provided then we change sales_cycles milestone to none
        and create a log that we deleted that particular milestone
        """
        if not milestone_id:
            self.milestone = None
            self.save()
            if not self.log.all():
                self.possibly_make_new()
            else:
                meta = self.log.last().meta
                sc_log_entry = SalesCycleLogEntry(
                    meta=meta,
                    entry_type=SalesCycleLogEntry.MD,
                    sales_cycle=self,
                    owner_id=user_id,
                    company_id=company_id
                    )
                sc_log_entry.save()
            return self


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
        if milestone.is_system == 0:
            self.possibly_make_pending()
        if milestone.is_system == 1:
            self.possibly_make_successful()
        if milestone.is_system == 2:
            self.possibly_make_failed()

        log_entries = self.log.filter(entry_type__in=[SalesCycleLogEntry.ME, SalesCycleLogEntry.MD])
        log_entries.delete()

        meta = {
            "prev_milestone_title": prev_milestone_title,
            "prev_milestone_color_code": prev_milestone_color_code,
            "next_milestone_title": milestone.title,
            "next_milestone_color_code": milestone.color_code
        }

        sc_log_entry = SalesCycleLogEntry(meta=json.dumps(meta),
                                          entry_type=SalesCycleLogEntry.MC,
                                          sales_cycle=self,
                                          owner_id=user_id, 
                                          company_id=company_id)
        sc_log_entry.save()
        return self

    def succeed(self, stats, user_id, company_id):
        amount = 0
        for product_id, value in stats.iteritems():
            amount += value
            s = SalesCycleProductStat.objects.get(sales_cycle=self,
                                                  product_id=product_id)
            s.real_value = value
            s.save()

        self.set_result_by_amount(amount, user_id, company_id, True)
        log_entry = SalesCycleLogEntry(
            sales_cycle=self, 
            meta=json.dumps({"amount": amount}),
            owner_id=user_id,
            company_id=company_id,
            entry_type = SalesCycleLogEntry.SC
        )
        log_entry.save()
        return self

    def fail(self, stats, user_id, company_id):
        amount = 0
        for product_id, value in stats.iteritems():
            amount += value
            s = SalesCycleProductStat.objects.get(sales_cycle=self,
                                                  product_id=product_id)
            s.projected_value = value
            s.save()

        self.set_result_by_amount(amount, user_id, company_id, False)
        log_entry = SalesCycleLogEntry(
            sales_cycle=self, 
            meta=json.dumps({"amount": amount}),
            owner_id=user_id,
            company_id=company_id,
            entry_type = SalesCycleLogEntry.FC
        )
        log_entry.save()
        return self

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
    attached_files = generic.GenericRelation('AttachedFile', null=True, blank=True)
    hashtags = generic.GenericRelation('HashTagReference', null=True, blank=True)

    class Meta:
        verbose_name = 'activity'
        db_table = settings.DB_PREFIX.format('activity')

    def __unicode__(self):
        return self.description

    @property
    def contact(self): # ????
        return self.sales_cycle.contact

    @property
    def comments_count(self):
        return self.comments.count()

    @classmethod
    def mark_as_read(cls, company_id, user_id, act_ids):
        return ActivityRecipient.objects.filter(
                company_id=company_id, user__id=user_id, activity__id__in=act_ids, has_read=False).update(has_read=True)

    @classmethod
    def get_filter_for_mobile(cls):
        month = (datetime.now(pytz.timezone(settings.TIME_ZONE)) - timedelta(days=7))
        return (
            Q(deadline__isnull=False, date_finished__isnull=True) |
            Q(deadline__isnull=False, date_finished__isnull=False, date_finished__gte=month) |
            Q(deadline__isnull=True,  date_edited__gte=month )
            )

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

    @classmethod
    def get_panel_info(cls, company_id, user_id):
        activity_q = Q(company_id=company_id, deadline__isnull=False)
        owner_q = Q(owner_id=user_id)

        period_q = {
            'days_q': Q(date_edited__gte=datetimeutils.get_start_of_today(timezone.now()), date_edited__lte=datetimeutils.get_end_of_today(timezone.now())),
            'weeks_q': Q(date_edited__gte=datetimeutils.get_start_of_week(timezone.now()), date_edited__lte=datetimeutils.get_end_of_week(timezone.now())),
            'months_q': Q(date_edited__gte=datetimeutils.get_start_of_month(timezone.now()), date_edited__lte=datetimeutils.get_end_of_month(timezone.now())),
        }

        total = Activity.objects.filter(activity_q)
        my_total = total.filter(owner_q)

        periods = ['days', 'weeks', 'months']

        def get_by_period(queryset):
            rv = {}
            for period in periods:
                period_total = queryset.filter(period_q[period+'_q'])
                rv[period] = period_total.count()
            return rv

        return {
                'all': {
                    'total': total.count(),
                    'completed': total.filter(Q(date_finished__isnull=False)).count(),
                    'overdue': total.filter(date_finished__isnull=True, deadline__lt=timezone.now().replace(hour=time.min.hour, minute=time.min.minute, second=time.min.second)).count(),
                    'by_period': get_by_period(total),
                },
                'my': {
                    'total': my_total.count(),
                    'completed': my_total.filter(Q(date_finished__isnull=False)).count(),
                    'overdue': my_total.filter(date_finished__isnull=True, deadline__lt=timezone.now().replace(hour=time.min.hour, minute=time.min.minute, second=time.min.second)).count(),
                    'by_period': get_by_period(my_total),
                },
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
        # установить статус цикла был новый, то пометить как открытый
        sales_cycle = instance.sales_cycle
        if sales_cycle.status == SalesCycle.NEW:
            sales_cycle.possibly_make_pending()
    
    @classmethod
    def after_delete(cls, sender, instance, **kwargs):
        # при удалении активити, если больше нет активити и нет этапа, то пометить как новый
        instance.sales_cycle.possibly_make_new()

    @classmethod
    def get_statistics(cls, company_id, user_id):
        company_feed = cls.company_feed(company_id=company_id, user_id=user_id)
        my_feed = cls.my_feed(company_id=company_id, user_id=user_id)
        return {
            'company_feed': {
                'count': company_feed['feed'].count(),
                'not_read': company_feed['not_read'],
            },
            'my_feed': {
                'count': my_feed['feed'].count(),
                'not_read': my_feed['not_read'],
            },
            'user_activities': cls.user_activities(company_id=company_id, user_id=user_id).count(),
            'my_tasks': cls.my_tasks(company_id=company_id, user_id=user_id).count(),
        }

    @classmethod
    def company_feed(cls, company_id, user_id):
        feed = Activity.objects.filter(company_id=company_id) \
                               .order_by('-date_edited')
        return {
            'feed': feed,
            'not_read': ActivityRecipient.objects.filter(activity_id__in=feed.values_list('id', flat=True),  \
                                                         user_id=user_id, \
                                                         has_read=False) \
                                                 .count(),
        }

    @classmethod
    def my_feed(cls, company_id, user_id):
        user = User.objects.get(id=user_id)
        account = user.accounts.get(company_id=company_id)
        contact_ids = Contact.objects.exclude(id__in=account.unfollow_list.all().values_list('id', flat=True)) \
                                     .values_list('id', flat=True)
        sales_cycle_ids = SalesCycle.objects.filter(contact_id__in=contact_ids)

        feed = Activity.objects.filter(company_id=company_id, sales_cycle_id__in=sales_cycle_ids) \
                               .order_by('-date_edited')

        return {
            'feed': feed,
            'not_read': ActivityRecipient.objects.filter(activity_id__in=feed.values_list('id', flat=True),  \
                                                         user_id=user_id, \
                                                         has_read=False) \
                                                 .count(),
        }

    @classmethod
    def user_activities(cls, company_id, user_id):
        return Activity.objects.filter(company_id=company_id, owner_id=user_id) \
                               .order_by('-date_edited')

    @classmethod
    def my_tasks(cls, company_id, user_id):
        return Activity.objects.filter(Q(company_id=company_id, deadline__isnull=False) & \
                                      (Q(owner_id=user_id, assignee__isnull=True) | Q(assignee_id=user_id))) \
                               .order_by('-date_edited')

    @classmethod
    def get_calendar(cls, company_id, user_id, dt):
        start = datetimeutils.get_start_of_month(dt)
        end = datetimeutils.get_end_of_month(dt)

        query = Q(company_id=company_id, owner_id=user_id)
        sub_query = Q(deadline__isnull=False, date_finished__isnull=True, deadline__gte=start, deadline__lte=end) | \
                    Q(deadline__isnull=False, date_finished__isnull=False, date_finished__gte=start, date_finished__lte=end) | \
                    Q(deadline__isnull=True, date_created__gte=start, date_created__lte=end)

        return Activity.objects.filter(query & sub_query)

    @classmethod
    def create_activity(cls, company_id, user_id, data):
        from .utils.parser import text_parser
        sales_cycle_id = data.get('sales_cycle_id', None) or \
                         Contact.objects.get(id=data.get('contact_id')).global_sales_cycle.id
        new_activity = Activity(description=data.get('description', ''),
                                sales_cycle_id=sales_cycle_id,
                                assignee_id=data.get('assignee_id', None),
                                deadline=dateutil.parser.parse(data.get('deadline', None)) if data.get('deadline', None) else None,
                                owner_id=user_id,
                                company_id=company_id,
                                need_preparation=data.get('need_preparation', False),)
        new_activity.save()

        account = Account.objects.get(company_id=company_id, user_id=user_id)

        new_activity.spray(company_id, account)

        text_parser(base_text=new_activity.description,
                    company_id=company_id,
                    content_class=new_activity.__class__,
                    object_id=new_activity.id)

        return new_activity
    
    @classmethod
    def search_by_hashtags(cls, company_id=None, search_query=None):
        hashtags = HASHTAG_PARSER.findall(search_query)
        activities = Activity.objects.filter(company_id=company_id)
        for hashtag in hashtags:
            activities = activities.filter(hashtags__hashtag__text=hashtag)
        return activities.order_by('date_created')


    def new_comments_count(self, user_id):
        return len(
            filter(lambda(comment): not comment.has_read(user_id),
                   self.comments.all())
            )

    def spray(self, company_id, account):
        accounts = []
        for account in Account.objects.filter(company_id=company_id):
            if not (self.contact in account.unfollow_list.all()):
                accounts.append(account)

        with transaction.atomic():
            for account in accounts:
                act_recip = ActivityRecipient(company_id=company_id, user=account.user, activity=self)
                if account.user.id==self.owner.id:
                    act_recip.has_read = True
                act_recip.save()

    def has_read(self, user_id):
        recip = self.recipients.filter(user_id=user_id).first()
        return not recip or recip.has_read

    def move(self, sales_cycle_id):
        prev_sales_cycle = self.sales_cycle
        new_sales_cycle = SalesCycle.objects.get(id=sales_cycle_id)
        self.sales_cycle = new_sales_cycle
        self.save()
        # новый цикл автоматически выставится как pending из-за after_save
        # а старый цикл нужно проверить и изменить статус
        prev_sales_cycle.possibly_make_new()
        return {
            'prev_sales_cycle': prev_sales_cycle,
            'new_sales_cycle': new_sales_cycle,
            'activity': self
        }

    def finish(self, result):
        self.result = result
        self.date_finished = timezone.now()
        self.save()
        return self

post_save.connect(Activity.after_save, sender=Activity)
post_delete.connect(Activity.after_delete, sender=Activity)


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

    @classmethod
    def mark_as_read(cls, company_id, user_id, comment_ids):
        return CommentRecipient.objects.filter(
                company_id=company_id, user__id=user_id, comment__id__in=comment_ids, has_read=False).update(has_read=True)

    @classmethod
    def build_new(cls, user_id, content_class=None,
                  object_id=None, save=False):
        comment = cls(owner_id=user_id)
        comment.content_type = ContentType.objects.get_for_model(content_class)
        comment.object_id = object_id
        if save:
            comment.save()
        return comment

    @classmethod
    def create_comment(cls, company_id, user_id, data):
        content_class =  ContentType.objects.get(app_label='alm_crm', 
                                                     model=data.pop('content_class').lower()
                                                    ).model_class()
        content_type = ContentType.objects.get_for_model(content_class)
        data['content_type'] = content_type
        comment = Comment(owner_id=user_id,
                          company_id=company_id,
                          **data)
        comment.save()

        account = Account.objects.get(company_id=company_id, user_id=user_id)
        comment.spray(company_id, account)

        return comment

    def spray(self, company_id, account):
        accounts = []
        for account in Account.objects.filter(company_id=company_id):
            if not (self.content_object.contact in account.unfollow_list.all()):
                accounts.append(account)
                
        with transaction.atomic():
            for account in accounts:
                com_recipient = CommentRecipient(company_id=company_id, user=account.user, comment=self)
                if account.user.id==self.owner.id:
                    com_recipient.has_read = True
                com_recipient.save()

    def has_read(self, user_id):
        recip = self.recipients.filter(user_id=user_id).first()
        return not recip or recip.has_read

    def save(self, **kwargs): # ???
        if self.date_created:
            self.date_edited = timezone.now()
        super(Comment, self).save(**kwargs)


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


class AttachedFile(SubscriptionObject):
    file_object = models.ForeignKey('almastorage.SwiftFile', related_name='attachments')
    owner = models.ForeignKey(User, related_name='owned_attachments', null=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s %s" % (self.file_object, self.content_object)

    @property
    def is_active(self):
        if self.content_object == None:
            return False
        return True

    @classmethod
    def build_new(cls, file_object, owner, company_id, content_class=None,
                  object_id=None, save=False):
        """TODO builds new AttachedFile objects with generic relation,
            and relation with SwiftFile object.

            arguments:
                file_object - SwiftFile object
                owner - User object, 
                company_id - Company id,
                content_class - class which be related with the model,
                object_id - related object id

        Returns
        --------
            attached_file - AttachedFile object
        """
        attached_file = cls(file_object=file_object, owner=owner, company_id=company_id)
        attached_file.content_type = ContentType.objects.get_for_model(content_class)
        attached_file.object_id = object_id
        if save:
            attached_file.save()
        return attached_file


def delete_related_file_objs(sender, instance, **kwargs):
    """TODO deletes swift file object on after attached_file deletes
        """
    file_obj = instance.file_object
    file_obj.delete()

signals.post_delete.connect(delete_related_file_objs, sender=AttachedFile)


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

    def __unicode__(self):
        return u'%s : %s -> %s' % (self.contact, self.share_from, self.share_to)

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
    def get_by_user(cls, company_id, user_id):
        shares = Share.objects.filter(company_id=company_id, share_to_id=user_id) \
                               .order_by('-date_created')
        return {
            'shares': shares,
            'not_read': shares.filter(is_read=False).count(),
        }

    @classmethod
    def mark_as_read(cls, company_id, user_id, ids):
        return Share.objects.filter(
                company_id=company_id, share_to=user_id, id__in=ids, is_read=False).update(is_read=True)

    @classmethod
    def search_by_hashtags(cls, company_id=None, search_query=None):
        hashtags = HASHTAG_PARSER.findall(search_query)
        shares = Share.objects.filter(company_id=company_id)
        for hashtag in hashtags:
            shares = shares.filter(hashtags__hashtag__text=hashtag)
        return shares.order_by('date_created')

    def __unicode__(self):
        return u'%s : %s -> %s' % (self.contact, self.share_from, self.share_to)
    
    @classmethod
    def create_share(cls, company_id, user_id, data):
        from .utils.parser import text_parser
        s = Share(
            note=data.get('note', ''),
            company_id=company_id,
            contact_id=data.get('contact_id'),
            share_from_id=user_id,
            share_to_id=data.get('share_to')
        )
        s.save()
        text_parser(base_text=s.note,
                    company_id = company_id,
                    content_class=s.__class__,
                    object_id=s.id)
        return s

signals.post_save.connect(
    Contact.upd_lst_activity_on_create, sender=Activity)
# signals.post_save.connect(
#     Contact.upd_status_when_first_activity_created, sender=Activity)
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

    def check_contact(self, contact_id):
        try:
            contact = self.contacts.get(id=contact_id)
            if contact is not None:
                return True
            else:
                return False
        except Contact.DoesNotExist:
            return False

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
    product = models.ForeignKey(Product, related_name='product_stats')
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
        ('allbase', _('all')),
        ('recent', _('recent')),
        ('coldbase', _('cold')),
        ('leadbase', _('lead')))
    title = models.CharField(max_length=100, default='')
    filter_text = models.CharField(max_length=500)
    owner = models.ForeignKey(User, related_name='owned_filter', null=True)
    base = models.CharField(max_length=8, choices=BASE_OPTIONS, default='allbase')

    class Meta:
        verbose_name = _('filter')
        db_table = settings.DB_PREFIX.format('filter')

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.base)

    def apply(self, company_id, user_id):
        from .filters import ContactFilter
        qs_case = {
            'allbase': Contact.get_all,
            'recent': Contact.get_recent_base,
            'coldbase': Contact.get_cold_base,
            'leadbase': Contact.get_lead_base,
        }

        queryset =  qs_case[self.base](company_id=company_id, user_id=user_id)

        return ContactFilter({'search': self.filter_text}, queryset)


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
    def build_new(cls, title=None, content_class=None, company_id=None, save=False):
        custom_field = cls(title=title, company_id=company_id)
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


class Notification(SubscriptionObject):
    # ACTIVITY_CREATION: при создании активити, {'count': N}

    type = models.CharField(blank=True, null=True, max_length=100)
    meta = models.TextField()
    owner = models.ForeignKey(User, related_name='notifications', null=True)