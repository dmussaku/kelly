# -*- coding: utf-8 -*-

import functools
from django.db import models, transaction, IntegrityError
from django.utils.translation import ugettext_lazy as _
from almanet import settings
from almanet.models import SubscriptionObject, Subscription
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
from alm_user.models import User
from django.template.loader import render_to_string
from django.db.models import signals, Q
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
import xlrd
import pytz


ALLOWED_TIME_PERIODS = ['week', 'month', 'year']

CURRENCY_OPTIONS = (
    ('USD', 'US Dollar'),
    ('RUB', 'Rubbles'),
    ('KZT', 'Tenge'),
)

GLOBAL_CYCLE_TITLE = 'Основной поток'
GLOBAL_CYCLE_DESCRIPTION = 'Автоматически созданный цикл'

def type_cast(input):
    return input if type(input) != float else str(input)

class CRMUser(SubscriptionObject):

    user_id = models.IntegerField(_('user id'))
    organization_id = models.IntegerField(_('organization id'))
    is_supervisor = models.BooleanField(_('is supervisor'), default=False)
    unfollow_list = models.ManyToManyField(
        'Contact', related_name='unfollowers',
        null=True, blank=True
        )

    def __unicode__(self):
        u = self.get_billing_user()
        return u and u.get_username() or None

    def get_billing_user(self, cache=False):
        """Returns a original user.
        Raises:
           User.DoesNotExist exception if no such relation exist"""
        
        if cache and hasattr(self, 'user'):
            return self.user

        user = User.objects.filter(pk=self.user_id).select_related('vcard').prefetch_related(
            'vcard__tel_set', 'vcard__category_set',
            'vcard__adr_set', 'vcard__title_set', 'vcard__url_set',
            'vcard__org_set', 'vcard__email_set',
            'vcard__custom_sections', 'vcard__custom_fields').first()
        if cache:
            self.user = user
        return user
        
    def set_supervisor(self, save=False):
        self.is_supervisor = True
        if save:
            self.save()

    def unset_supervisor(self, save=False):
        self.is_supervisor = False
        if save:
            self.save()

    @classmethod
    def get_crmusers(cls, subscription_id, with_users=False):
        """TEST Returns list of crmusers on with
            Returns:
                Queryset<CRMUser>
                if with_users:
                    Queryset<User>
            example: (crmusers, users)
        """
        crmusers = cls.objects.filter(subscription_id=subscription_id)
        if with_users:
            users = User.objects.filter(
                id__in=crmusers.values_list('user_id', flat=True))
            return (crmusers, users)
        else:
            return crmusers

    @classmethod
    def get_subscription_id(cls, user_id):
        return cls.objects.get(id=user_id).subscription_id


class Milestone(SubscriptionObject):

    title = models.CharField(_("title"), max_length=1024, null=True, blank=True)
    color_code = models.CharField(_('color code'), max_length=1024, null=True, blank=True)

    class Meta:
        verbose_name = _('milestone')
        db_table = settings.DB_PREFIX.format('milestone')

    @classmethod
    def get_for_subscr(cls, subscr_id):
        return cls.objects.filter(subscription_id=subscr_id)

    @classmethod
    def create_default_milestones(cls, subscription_id):
        milestones = []
        default_data = [{'title':'Звонок/Заявка', 'color_code': '#F4B59C'},
                        {'title':'Отправка КП', 'color_code': '#F59CC8'},
                        {'title':'Согласование договора', 'color_code': '#A39CF4'},
                        {'title':'Выставление счета', 'color_code': '#9CE5F4'},
                        {'title':'Контроль оплаты', 'color_code': '#9CF4A7'},
                        {'title':'Предоставление услуги', 'color_code': '#D4F49B'},
                        {'title':'Upsales', 'color_code': '#F4DC9C'}]

        for data in default_data:
            milestone = Milestone()
            milestone.title = data['title']
            milestone.color_code = data['color_code']
            milestone.subscription_id = subscription_id
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
        CRMUser, related_name='owned_contacts',
        null=True, blank=True)

    latest_activity = models.OneToOneField(
        'Activity', on_delete=models.SET_NULL,
        related_name='contact_latest_activity', null=True)
    mentions = generic.GenericRelation('Mention')
    comments = generic.GenericRelation('Comment')

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

    def to_vcard(self, locale='ru_RU'):
        return self.vcard.exportTo('vcard')

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
    def share_contact(cls, share_from, share_to, contact_id, comment=None):
        return cls.share_contacts(share_from, share_to, [contact_id], comment)

    @classmethod
    def share_contacts(cls, share_from, share_to, contact_ids, comment=None):
        '''
        Share multiple contacts to a single user
        '''
        assert isinstance(contact_ids, (list, tuple)), 'Must be a list'
        if not contact_ids:
            return False
        try:
            share_from = CRMUser.objects.get(id=share_from)
            share_to = CRMUser.objects.get(id=share_to)
            contacts = Contact.objects.filter(id__in=contact_ids)
            share_list = []
            for contact in contacts:
                share = Share(
                        share_from=share_from,
                        share_to=share_to,
                        contact=contact
                    )
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
                        content_type_id=ContentType.objects.get_for_model(Share).id
                        )
                    comment.save()
            return True
        except:
            return False

    def create_share_to(self, user_id, note=None):
        default_note = self.SHARE_IMPORTED_TEXT + \
            self.date_created.strftime(settings.DATETIME_FORMAT_NORMAL)

        share = Share(
            note=note or default_note,
            share_to_id=user_id,
            share_from_id=user_id,
            contact_id=self.id
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
    def get_contacts_by_status(cls, subscription_id, status):
        q = Q(subscription_id=subscription_id)
        q &= Q(status=status)
        return Contact.objects.filter(q).order_by('-date_created')

    @classmethod
    def get_contacts_for_last_activity_period(
            cls, user_id, from_dt=None, to_dt=None):
        r"""
        Retrieves all contacts according to the following criteria:
            - user contacted for that time period (`from_dt`, `to_dt`)
        user contacted means user have activities with at least one
        contact for that period.

        Parameters
        ----------
           user_id - who is contacted
           from_dt - date from
           to_dt - date to

        Returns
        -------
        Queryset of Contacts with whom `user_id` get contacted for that period.
        """
        crm_user = CRMUser.objects.get(id=user_id)

        # there is no need in filter by subscription_id
        q = Q(date_created__range=(from_dt, to_dt))
        activities = crm_user.activity_owner.filter(q)
        contact_ids = activities.values_list('sales_cycle__contact_id', flat=True)
        return Contact.objects.filter(id__in=contact_ids)

    @classmethod
    def filter_contacts_by_vcard(cls, subscription_id, search_text,
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
            q = Q(subscription_id=subscription_id)
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
            #         **{'subscription_id': contacts.subscription_id,
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
    def import_from_vcard(cls, raw_vcard, creator):
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
                c.save()
                SalesCycle.create_globalcycle(
                    **{'subscription_id': c.subscription_id,
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
                c.owner = creator.get_crmuser()
                c.subscription_id = creator.get_crmuser().subscription_id
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
                        **{'subscription_id':c.subscription_id,
                         'owner_id':creator.get_crmuser().id,
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



    @classmethod
    @transaction.atomic
    def import_from_xls(cls, xls_file_data, creator):
        book = xlrd.open_workbook(file_contents=xls_file_data)
        sheets_left = True
        contacts = []
        sid = transaction.savepoint()
        for sheet in book.sheets():
            i = 1
            header_row = sheet.row(0)
            while(sheets_left):
                try:
                    data = sheet.row(i)
                except IndexError:
                    sheets_left = False
                    continue
                c = cls()
                v = VCard()
                try:
                    with transaction.atomic():
                        v.family_name = data[0].value if type(data[0].value) == unicode else str(data[0].value)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i,1)
                try:
                    with transaction.atomic():
                        v.given_name = data[1].value if type(data[1].value) == unicode else str(data[1].value)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i,2)
                try:
                    with transaction.atomic():
                        v.additional_name = data[2].value if type(data[2].value) == unicode else str(data[2].value)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i,3)
                v.fn = v.given_name+" "+v.family_name
                if ((not v.given_name) and (not v.family_name) and data[4].value):
                    try:
                        with transaction.atomic():
                            v = VCard(fn=data[4].value)
                            v.save()
                            c = cls(vcard=v, tp='co')
                    except IntegrityError:
                        transaction.savepoint_rollback(sid)
                        return (i,5)
                    c.owner = creator.get_crmuser()
                    c.subscription_id = creator.get_crmuser().subscription_id
                    c.save()
                if not v.id:
                    v.save()
                    c.vcard = v
                    c.owner = creator.get_crmuser()
                    c.subscription_id = creator.get_crmuser().subscription_id
                    c.save()
                SalesCycle.create_globalcycle(**{
                    'subscription_id':c.subscription_id,
                    'owner_id': c.owner_id,
                    'contact_id': c.id
                })
                try:
                    with transaction.atomic():
                        if data[3].value:
                            positions = type_cast(data[3].value).split(';')
                            for position in positions:
                                title = Title(
                                    vcard=v,
                                    data=position
                                    )
                                title.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 4)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[4].value:
                            org = Org(vcard=v)
                            org.organization_name = type_cast(data[4].value)
                            try:
                                with transaction.atomic():
                                    if data[5].value:
                                        org.organization_unit = type_cast(data[5].value)
                                    org.save()
                            except IntegrityError:
                                transaction.savepoint_rollback(sid)
                                return (i, 6)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 5)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[6].value:
                            phones = type_cast(data[6].value).split(';')
                            for phone in phones:
                                tel = Tel(vcard=v, type='WORK')
                                tel.value = phone
                                tel.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i,7)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[7].value:
                            phones = type_cast(data[7].value).split(';')
                            for phone in phones:
                                tel = Tel(vcard=v, type='cell')
                                tel.value = phone
                                tel.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 8)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[8].value:
                            phones = type_cast(data[8].value).split(';')
                            for phone in phones:
                                tel = Tel(vcard=v, type='xadditional')
                                tel.value = phone
                                tel.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 9)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[9].value:
                            phones = type_cast(data[9].value).split(';')
                            for phone in phones:
                                tel = Tel(vcard=v, type='fax')
                                tel.value = phone
                                tel.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 10)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[10].value:
                            emails = type_cast(data[10].value).split(';')
                            for email_str in emails:
                                email = Email(vcard=v, type='work')
                                email.value = email_str
                                email.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 11)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[11].value:
                            emails = type_cast(data[11].value).split(';')
                            for email_str in emails:
                                email = Email(vcard=v, type='internet')
                                email.value = email_str
                                email.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 12)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[12].value:
                            adresses = type_cast(data[12].value).split(';;')
                            for address_str in adresses:
                                addr_objs = address_str.split(';')
                                addr_objs = [v,'POSTAL'] + addr_objs
                                address = Adr.create_from_list(addr_objs)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 13)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[13].value:
                            adresses = type_cast(data[13].value).split(';;')
                            for address_str in adresses:
                                addr_objs = address_str.split(';')
                                addr_objs = [v,'xlegal'] + addr_objs
                                address = Adr.create_from_list(addr_objs)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 14)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[14].value:
                            adresses = type_cast(data[14].value).split(';;')
                            for address_str in adresses:
                                addr_objs = address_str.split(';')
                                addr_objs = [v,'WORK'] + addr_objs
                                address = Adr.create_from_list(addr_objs)
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 15)
                except IndexError:
                    pass
                try:
                    with transaction.atomic():
                        if data[15].value:
                            sites = type_cast(data[15].value).split(';')
                            for site in sites:
                                url = Url(
                                    vcard=v,
                                    type='website',
                                        value=site
                                        )
                                url.save()
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    return (i, 16)
                except IndexError:
                    pass
                contacts.append(c)
                # print "%s created contact %s" % (c, c.id)
                i = i+1
        transaction.savepoint_commit(sid)
        return contacts

    @classmethod
    def get_contacts_by_last_activity_date(
            cls, subscription_id, user_id=None, owned=True, mentioned=False,
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
        q0 = Q(subscription_id=subscription_id)
        q = Q()
        if not all:
            if owned:
                q |= Q(owner_id=user_id)
            if mentioned:
                q |= Q(mentions__user_id=user_id)
            if in_shares:
                crmuser = CRMUser.objects.get(pk=user_id)
                shares = crmuser.in_shares
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
    def get_cold_base(cls, subscription_id):
        """Returns list of contacts that are considered cold.
        Cold contacts should satisfy two conditions:
            1. no assignee for contact
            2. status is NEW"""
        q = Q(subscription_id=subscription_id)
        q &= Q(status=cls.NEW)
        return cls.objects.filter(q).order_by('-date_created')


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
    owner = models.ForeignKey('CRMUser', null=True, blank=True,
                              related_name='owned_values')

    class Meta:
        verbose_name = 'value'
        db_table = settings.DB_PREFIX.format('value')

    def __unicode__(self):
        return "%s %s %s" % (self.amount, self.currency, self.salary)

    @classmethod
    def get_values(cls, subscription_id):
        q = Q(subscription_id=subscription_id)
        return cls.objects.filter(q)


class Product(SubscriptionObject):
    name = models.CharField(_('product name'), max_length=100, blank=False)
    description = models.TextField(_('product description'))
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS,
                                default='KZT')
    owner = models.ForeignKey('CRMUser', related_name='crm_products',
                              null=True, blank=True)
    custom_sections = generic.GenericRelation('CustomSection')
    custom_fields = generic.GenericRelation('CustomField')


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
        self.owner = CRMUser.objects.get(id=author_id)

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
    def get_products(cls, subscription_id):
        q = Q(subscription_id=subscription_id)
        return cls.objects.filter(q).order_by('-date_created')

    @classmethod
    @transaction.atomic()
    def import_from_xls(cls, xls_file_data, creator):
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
                subscription_id=creator.get_crmuser().subscription_id,
                owner=creator.get_crmuser()
                )
            if row_vals[1]:
                product.description = row_vals[1]
            if row_vals[2]:
                product.price = row_vals[2]
            else:
                product.price = 0
            product.save()
            for i in range(0, len(row_vals[3:])):
                if row_vals[i]:
                    field = CustomField.build_new(
                        title=col_names[i],
                        value=row_vals[i],
                        content_class=Product,
                        object_id=product.id,
                        save=True
                        )
            product_list.append(product)
        return product_list

class ProductGroup(SubscriptionObject):
    owner = models.ForeignKey(CRMUser, related_name='owned_product_groups', blank=True, null=True)
    title = models.CharField(max_length=150)
    products = models.ManyToManyField(Product, related_name='product_groups',
                                   null=True, blank=True)

    class Meta:
        verbose_name = _('product_group')
        db_table = settings.DB_PREFIX.format('product_group')

    def __unicode__(self):
        return self.title

    @classmethod
    def get_for_subscr(cls, subscr_id):
        return cls.objects.filter(subscription_id=subscr_id)


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
    owner = models.ForeignKey(CRMUser, related_name='owned_sales_cycles')
    followers = models.ManyToManyField(
        CRMUser, related_name='follow_sales_cycles',
        null=True, blank=True)
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
    def get_global(cls, subscription_id, contact_id):
        return SalesCycle.objects.get(subscription_id=subscription_id, contact_id=contact_id,
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
                                    subscription_id=kwargs['subscription_id'])
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
            self.owner = CRMUser.objects.get(id=user_id)
            if save:
                self.save()
            return True
        except CRMUser.DoesNotExist:
            return False

    def get_activities(self):
        """TEST Returns list of activities ordered by date."""
        return self.rel_activities.order_by('-date_created')

    def get_mentioned_users(self):
        user_ids = self.mentions.values_list('user_id', flat=True)
        return CRMUser.objects.filter(pk__in=user_ids)

    def get_first_activity_date(self):
        a = self.rel_activities.order_by('date_created').first()
        return a and a.date_created

    def get_last_activity_date(self):
        a = self.rel_activities.order_by('-date_created').first()
        return a and a.date_created

    def add_product(self, product_id, **kw):
        """TEST Assigns products to salescycle"""
        return self.add_products([product_id], **kw)

    def add_products(self, product_ids):
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
                s = SalesCycleProductStat(sales_cycle=self, product=product)
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

    def set_result_by_amount(self, amount):
        v = Value(amount=amount, owner=self.owner)
        v.save()

        self.real_value = v
        self.save()

    def add_follower(self, user_id, **kw):
        """TEST Set follower to salescycle"""
        return self.add_followers([user_id], **kw)[0]

    def add_followers(self, user_ids, save=False):
        """TEST Set followers to salescycle"""
        assert isinstance(user_ids, (tuple, list)), 'must be a list'
        status = []
        for uid in user_ids:
            try:
                crm_user = CRMUser.objects.get(id=uid)
                self.followers.add(crm_user)
                status.append(True)
            except CRMUser.DoesNotExist:
                status.append(False)
        return status

    def change_milestone(self, crmuser, milestone_id, meta):
        milestone = Milestone.objects.get(id=milestone_id)
        self.milestone = milestone
        self.save()

        sc_log_entry = SalesCycleLogEntry(meta=meta,
                                          entry_type=SalesCycleLogEntry.MC,
                                          sales_cycle=self,
                                          owner=crmuser)
        sc_log_entry.save()
        return self

    def close(self, products_with_values):
        amount = 0
        for product, value in products_with_values.iteritems():
            amount += value
            s = SalesCycleProductStat.objects.get(sales_cycle=self,
                                                  product=Product.objects.get(id=product))
            s.value = value
            s.save()

        self.status = self.COMPLETED
        self.set_result_by_amount(amount)
        self.save()

        activity = Activity(
            sales_cycle=self,
            owner=self.owner,
            description=_('Closed. Amount Value is %(amount)s') % {'amount': amount}
            )
        activity.save()
        activity.set_feedback_status(Feedback.OUTCOME, save_feedback=True)
        return [self, activity]

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
        cls, subscription_id, user_id=None, owned=True, mentioned=False,
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
        q0 = Q(subscription_id=subscription_id)
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
            sales_cycles = SalesCycle.objects.filter(q0 & q).order_by(
                '-latest_activity__date_created')

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


class SalesCycleLogEntry(SubscriptionObject):
    TYPES_CAPS = (
        _('Milestone change'),
    )
    TYPES = (MC, ) = ('MC', )
    TYPES_OPTIONS = zip(TYPES, TYPES_CAPS)
    TYPES_DICT = dict(zip(('MC', ), TYPES))

    meta = models.TextField(null=True, blank=True)
    sales_cycle = models.ForeignKey(SalesCycle, related_name='log')
    entry_type = models.CharField(max_length=2,
                              choices=TYPES_OPTIONS, default=MC)
    owner = models.ForeignKey(CRMUser, related_name='owner', null=True)


class Activity(SubscriptionObject):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField(blank=True, null=True)
    date_finished = models.DateTimeField(blank=True, null=True)
    need_preparation = models.BooleanField(default=False, blank=True)
    sales_cycle = models.ForeignKey(SalesCycle, related_name='rel_activities')
    owner = models.ForeignKey(CRMUser, related_name='activity_owner')
    mentions = generic.GenericRelation('Mention', null=True)
    comments = generic.GenericRelation('Comment', null=True)
    hashtags = generic.GenericRelation('HashTagReference')

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
        self.owner = CRMUser.objects.get(id=author_id)

    @property
    def contact(self):
        return self.sales_cycle.contact

    @property
    def feedback_status(self):
        if hasattr(self, 'feedback'):
            return self.feedback.status
        return None

    @property
    def comments_count(self):
        return self.comments.count()

    def set_feedback(self, feedback_obj, save=False):
        """Set feedback to activity instance. Saves if `save` is set(True)."""
        feedback_obj.activity = self
        if save:
            feedback_obj.save()

    def set_feedback_status(self, status, save_feedback=False):
        if not hasattr(self, 'feedback'):
            self.feedback = Feedback(
                activity=self,
                owner=self.owner
                )
        self.feedback.status = status
        if save_feedback:
            self.feedback.save()

    def spray(self, subscription_id):
        unfollow_set = {
            unfollower.id for unfollower
            in self.sales_cycle.contact.unfollowers.all()}

        q = Q(subscription_id=subscription_id)
        university_set = set(CRMUser.objects.filter(q).values_list(
                             'id', flat=True))
        followers = CRMUser.objects.filter(
            pk__in=(university_set - unfollow_set))

        with transaction.atomic():
            for follower in followers:
                act_recip = ActivityRecipient(user=follower, activity=self)
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
        month = (datetime.now(pytz.timezone(settings.TIME_ZONE)) - timedelta(days=31))
        return (
            Q(deadline__isnull=False, date_finished__isnull=True) |
            Q(deadline__isnull=False, date_finished__isnull=False, date_finished__gte=month) |
            Q(deadline__isnull=True,  date_edited__gte=month )
            )

    @classmethod
    def get_activities_by_contact(cls, contact_id):
        return Activity.objects.filter(sales_cycle__contact_id=contact_id)

    @classmethod
    def get_user_activities(cls, user):
        return cls.objects.filter(owner=user).order_by('-date_created')

    @classmethod
    def get_activities_by_salescycle(cls, sales_cycle_id):
        return cls.objects.filter(sales_cycle_id=sales_cycle_id).order_by('-date_created')

    @classmethod
    def get_activities_by_subscription(cls, subscription_id):
        return cls.objects.filter(subscription_id=subscription_id)\
            .order_by('date_created')

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
            crmuser = CRMUser.objects.get(id=user_id)
        except CRMUser.DoesNotExist:
            return False
        '''
        need to implement the conversion to datetime object
        from input arguments
        '''
        if (type(from_dt) and type(to_dt) == datetime):
            pass
        activity_queryset = Activity.objects.filter(
            date_created__gte=from_dt, date_created__lte=to_dt, owner=crmuser)
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
        cls, subscription_id, user_id=None, owned=True,
        mentioned=False, all=False, include_sales_cycles=False):
        """Returns activities where crmuser is owner or mentioned
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
        q0 = Q(subscription_id=subscription_id)
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


class ActivityRecipient(SubscriptionObject):
    activity = models.ForeignKey(Activity, related_name='recipients')
    user = models.ForeignKey(CRMUser, related_name='activities')
    has_read = models.BooleanField(default=False)

    @property
    def owner(self):
        return self.activity.owner

    class Meta:
        db_table = settings.DB_PREFIX.format('activity_recipient')

    def __unicode__(self):
        return u'Activity: %s' % self.pk or 'Unknown'


class Feedback(SubscriptionObject):
    STATUSES_CAPS = (
        _('Waiting'),
        _('Outcome'),
        _('Client is happy'),
        _('Client is OK'),
        _('Client is angry'))
    STATUSES = (WAITING, OUTCOME, POSITIVE, NEUTRAL, NEGATIVE) = ('W', '$', '1', '2', '3')
    STATUSES_OPTIONS = zip(STATUSES, STATUSES_CAPS)
    STATUSES_DICT = dict(zip(('WAITING', 'OUTCOME', 'POSITIVE', 'NEUTRAL', 'NEGATIVE'),
                         STATUSES))

    feedback = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=1, choices=STATUSES_OPTIONS, default=WAITING)
    activity = models.OneToOneField(Activity)
    value = models.OneToOneField(Value, blank=True, null=True)
    mentions = generic.GenericRelation('Mention')
    comments = generic.GenericRelation('Comment')
    owner = models.ForeignKey(CRMUser, related_name='feedback_owner')

    def __unicode__(self):
        return u"%s: %s" % (self.activity, self.status)

    def statusHuman(self):
        statuses = filter(lambda x: x[0] == self.status, self.STATUSES_OPTIONS)
        return len(statuses) > 0 and statuses[0] or None

    def save(self, **kwargs):
        if self.date_created:
            self.date_edited = timezone.now()
        super(Feedback, self).save(**kwargs)


class Mention(SubscriptionObject):
    user = models.ForeignKey(CRMUser, related_name='mentions', null=True)
    owner = models.ForeignKey(CRMUser, related_name='owned_mentions', null=True)
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
                  object_id=None, save=False):
        mention = cls(user_id=user_id)
        mention.content_type = ContentType.objects.get_for_model(content_class)
        mention.object_id = object_id
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

    def save(self, **kwargs):
        if not self.subscription_id and self.content_object:
            self.subscription_id = self.content_object.owner.subscription_id
        super(SubscriptionObject, self).save(**kwargs)



class Comment(SubscriptionObject):
    comment = models.CharField(max_length=140)
    owner = models.ForeignKey(CRMUser, related_name='comment_owner')
    object_id = models.IntegerField(null=True, blank=False)
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    mentions = generic.GenericRelation('Mention')
    hashtags = generic.GenericRelation('HashTagReference')

    def __unicode__(self):
        return "%s's comment" % (self.owner)

    @property
    def author(self):
        return self.owner

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


class Share(SubscriptionObject):
    is_read = models.BooleanField(default=False, blank=False)
    contact = models.ForeignKey(Contact, related_name='share_set', blank=True, null=True)
    share_to = models.ForeignKey(CRMUser, related_name='in_shares')
    share_from = models.ForeignKey(CRMUser, related_name='owned_shares')
    comments = generic.GenericRelation('Comment')
    note = models.CharField(max_length=500, null=True)
    hashtags = generic.GenericRelation('HashTagReference')
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
    def get_shares(cls, subscription_id):
        q = Q(subscription_id=subscription_id)
        return cls.objects.filter(q).order_by('-date_created')

    @classmethod
    def get_shares_in_for(cls, user_id):
        return cls.objects.filter(share_to__pk=user_id)\
            .order_by('-date_created')

    @classmethod
    def get_shares_owned_for(cls, user_id):
        return cls.objects.filter(share_from__pk=user_id)\
            .order_by('-date_created')

    def __unicode__(self):
        return u'%s : %s -> %s' % (self.contact, self.share_from, self.share_to)


def parse_note_text(sender, instance=None, **kwargs):
    from utils.parser import text_parser
    for note in Note.objects.filter(vcard = instance.vcard):
        text_parser(base_text=note.data, content_class=instance.__class__,
                    object_id=instance.id)

signals.post_save.connect(
    Contact.upd_lst_activity_on_create, sender=Activity)
signals.post_save.connect(parse_note_text, sender=Contact)
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
    milestones = Milestone.create_default_milestones(instance.id)

def delete_related_milestones(sender, instance, **kwargs):
    for milestone in Milestone.objects.filter(subscription_id=instance.id):
        milestone.delete()

signals.post_delete.connect(on_activity_delete, sender=Activity)
signals.pre_save.connect(check_is_title_empty, sender=SalesCycle)
signals.post_save.connect(create_milestones, sender=Subscription)
signals.pre_delete.connect(delete_related_milestones, sender=Subscription)

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
    owner = models.ForeignKey(CRMUser, related_name='owned_list', blank=True, null=True)
    title = models.CharField(max_length=150)
    contacts = models.ManyToManyField(Contact, related_name='contact_list',
                                   null=True, blank=True)

    class Meta:
        verbose_name = _('contact_list')
        db_table = settings.DB_PREFIX.format('contact_list')

    def __unicode__(self):
        return self.title

    @classmethod
    def get_for_subscr(cls, subscr_id):
        return cls.objects.filter(subscription_id=subscr_id)

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
    value = models.IntegerField(default=0)

    @property
    def owner(self):
        return self.sales_cycle.owner

    class Meta:
        verbose_name = _('sales_cycle_product_stat')
        db_table = settings.DB_PREFIX.format('cycle_prod_stat')

    def __unicode__(self):
        return u'%s | %s | %s' % (self.sales_cycle, self.product, self.value)


class Filter(SubscriptionObject):
    BASE_OPTIONS = (
        ('AL', _('all')),
        ('RT', _('recent')),
        ('CD', _('cold')),
        ('LD', _('lead')))
    title = models.CharField(max_length=100, default='')
    filter_text = models.CharField(max_length=500)
    owner = models.ForeignKey(CRMUser, related_name='owned_filter')
    base = models.CharField(max_length=6, choices=BASE_OPTIONS, default='all')

    class Meta:
        verbose_name = _('filter')
        db_table = settings.DB_PREFIX.format('filter')

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.base)

    def save(self, **kwargs):
        if not self.subscription_id and self.owner:
            self.subscription_id = self.owner.subscription_id
        super(self.__class__, self).save(**kwargs)

    @classmethod
    def get_filters_by_crmuser(cls, crmuser_id):
        return Filter.objects.filter(owner=crmuser_id)


class HashTag(models.Model):
    text = models.CharField(max_length=500, unique=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        verbose_name = _('hashtag')
        db_table = settings.DB_PREFIX.format('hashtag')

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
                  object_id=None, save=False):
        hashtag_reference = cls(hashtag_id=hashtag_id)
        hashtag_reference.content_type = ContentType.objects.get_for_model(content_class)
        hashtag_reference.object_id = object_id
        if save:
            hashtag_reference.save()
        return hashtag_reference

    def save(self, **kwargs):
        if not self.subscription_id and self.content_object:
            self.subscription_id = self.content_object.owner.subscription_id
        super(SubscriptionObject, self).save(**kwargs)


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
    value = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    section = models.ForeignKey('CustomSection', related_name='custom_fields', null=True, blank=True)

    @property
    def owner(self):
        if self.section:
            return self.section.owner
        if self.content_object.__class__ == VCard:
            return self.content_object.contact.owner
        return self.content_object.owner

    class Meta:
        verbose_name = _('custom_field')
        db_table = settings.DB_PREFIX.format('custom_fields')

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.value)

    @classmethod
    def build_new(cls, section=None, title=None, value=None, content_class=None,
                  object_id=None, save=False):
        custom_field = cls(title=title, value=value)
        if section:
            custom_field.section=section
            custom_field.content_type = section.content_type
            custom_field.object_id = section.object_id
        if content_class and object_id:
            custom_field.content_type = ContentType.objects.get_for_model(content_class)
            custom_field.object_id = object_id
        if save:
            custom_field.save()
        return custom_field
