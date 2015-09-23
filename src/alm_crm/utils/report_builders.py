#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from alm_crm.models import (
    SalesCycle,
    Milestone,
    Activity,
    SalesCycleProductStat,
    Product,
    ProductGroup,
    SalesCycleLogEntry,
    Milestone
    )
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
import pytz
import xlsxwriter
from dateutil import tz

def build_funnel(company_id, data=None):
    data = {} if data is None else data
    rv = {
        'report_name': 'funnel'
    }
    q = Q(products__isnull=False,
            company_id=company_id,
            is_global=False)

    if 'products' in data:
        q &= Q(products__pk__in=data.get('products', []))

    sales_cycles = list(set(SalesCycle.objects.filter(q)))

    rv['total'] = len(sales_cycles)
    rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))
    rv['funnel'] = {}
    milestones = Milestone.objects.filter(company_id=company_id)
    system_milestones = milestones.filter(is_system__in=[1,2]).order_by('is_system')
    milestones = milestones.exclude(is_system__in=[1,2]).order_by('sort')
    sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
    for m in milestones:
        rv['funnel'][m.id] = [sc.id for sc in sc_in_funnel]
        sc_in_funnel = [sc for sc in sc_in_funnel if sc.milestone.id != m.id]
    for m in system_milestones:
        rv['funnel'][m.id] = [sc.id for sc in sales_cycles if sc.milestone_id == m.id]
    return rv

def build_realtime_funnel(company_id, data={}):
    rv = {
        'report_name': 'realtime_funnel'
    }
    q = Q(products__isnull=False,
            company_id=company_id,
            is_global=False)

    if 'products' in data:
        q &= Q(products__pk__in=data.get('products', []))

    sales_cycles = list(set(SalesCycle.objects.filter(q)))

    rv['total'] = len(sales_cycles)

    rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))

    rv['funnel'] = {}
    milestones = Milestone.objects.filter(company_id=company_id)

    sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
    for m in milestones:
        rv['funnel'][m.id] = [sc.id for sc in sc_in_funnel if sc.milestone.id == m.id]
    return rv

def build_activity_feed(company_id, data=None, timezone='UTC'):
    data = {} if data is None else data
    rv = {
        'report_name': 'activity_feed'
    }
    q = Q(company_id=company_id)

    if 'users' in data:
        q &= Q(owner_id__in=data.get('users', []))
    if 'date_from' in data:
        q &= Q(date_created__gte=data.get('date_from', datetime.now()))
    if 'date_to' in data:
        q &= Q(date_created__lte=data.get('date_to', datetime.now()))
    if 'sort' in data and 'order' in data:
        _order = '-' if data.get('order') == 'desc' else ''
        _sortBy = 'date_created' if data.get('sort') == 'date' else 'owner__vcard__fn'
        order_q = _order + _sortBy

    report_data = []
    months = [
        u'Янв',
        u'Фев',
        u'Мар',
        u'Апр',
        u'Май',
        u'Июн',
        u'Июл',
        u'Авг',
        u'Сен',
        u'Окт',
        u'Ноя',
        u'Дек'
    ]
    cnt = 1

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(timezone)

    for activity in Activity.objects.filter(q).order_by(order_q):
        date_created_utc = activity.date_created
        date_created_utc = date_created_utc.replace(tzinfo=from_zone)
        date_local = date_created_utc.astimezone(to_zone)
        date = date_local.strftime("%H:%M, %d {%m} %y")
        month = date.split('{')[1].split('}')[0]
        date = date.split('{')[0]+months[int(month)-1]+date.split('}')[1]

        row = {
            'number': cnt,
            'date': date,
            'hashtags': [hr.hashtag.text for hr in activity.hashtags.all()],
            'description': activity.description,
            'contact': activity.sales_cycle.contact.vcard.fn,
            'user': activity.owner.get_full_name()
        }
        report_data.append(row)
        cnt += 1

    rv['report_data'] = report_data

    return rv


def get_activity_feed_xls(company_id, data=None, timezone='UTC'):
    report_data = build_activity_feed(company_id, data, timezone)['report_data']

    from  tempfile import NamedTemporaryFile

    f = NamedTemporaryFile(delete=True)

    workbook = xlsxwriter.Workbook(f.name)
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format({'bold': True})
    header_format.set_border(style=1)
    header_format.set_text_wrap()

    cell_format = workbook.add_format()
    cell_format.set_border(style=1)
    cell_format.set_text_wrap()

    worksheet.write(0, 0, u'№', header_format)
    worksheet.write(0, 1, u'Дата', header_format)
    worksheet.write(0, 2, u'Хэштеги', header_format)
    worksheet.write(0, 3, u'Описание', header_format)
    worksheet.write(0, 4, u'Наименование контакта', header_format)
    worksheet.write(0, 5, u'Пользователь', header_format)

    row = 1

    for item in report_data:
        hashtags = ''
        hstg_len = len(item['hashtags']) - 1
        for cnt, hashtag in enumerate(item['hashtags']):
            if cnt < hstg_len:
                hashtag = hashtag + ','

            hashtags += hashtag

        worksheet.write(row, 0, item['number'], cell_format)
        worksheet.write(row, 1, item['date'], cell_format)
        worksheet.write(row, 2, hashtags, cell_format)
        worksheet.write(row, 3, item['description'], cell_format)
        worksheet.write(row, 4, item['contact'], cell_format)
        worksheet.write(row, 5, item['user'], cell_format)
        row+=1

    worksheet.set_column(0, 0, 5)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 25)
    worksheet.set_column(3, 3, 30)
    worksheet.set_column(4, 4, 25)
    worksheet.set_column(5, 5, 25)

    workbook.close()

    return f


def build_user_report(company_id, data):
    user_ids=data.get('user_ids', [-1])
    from_date=data.get('from_date', None)
    to_date=data.get('to_date', None)
    if from_date == None:
        from_date = datetime(2014, 1, 1).replace(tzinfo=pytz.UTC)

    if to_date == None:
        to_date = datetime.now().replace(tzinfo=pytz.UTC)

    open_sales_cycles = SalesCycle.objects.filter(owner_id__in=user_ids if user_ids[0] != -1
                                                    else CRMUser.objects.filter(company_id=company_id).values_list('id', flat=True),
                                                    status__in=['N', 'P'],
                                                    date_created__range=(from_date, to_date), is_global=False)
    close_activities = Activity.objects.filter(owner_id__in=user_ids, description__startswith='Closed')
    closed_sales_cycles = SalesCycle.objects.filter(status__in='C', rel_activities__in=close_activities, date_created__range=(from_date, to_date), is_global=False)
    earned_money = sum(SalesCycleProductStat.objects.filter(
        sales_cycle__in=closed_sales_cycles).values_list('real_value', flat=True))

    activity_dates = Activity.objects.filter(owner_id__in=user_ids if user_ids[0] != -1
                                                    else CRMUser.objects.filter(company_id=company_id).values_list('id',
                                                        flat=True), date_created__range=(from_date, to_date)).order_by('date_created').values_list(
                                                        'date_created', flat=True)
    activity_heatmap = []
    current_date = activity_dates.first() if activity_dates.count() > 0 else None
    if current_date != None:
        cnt = 1
        for date in activity_dates:
            if date.day != current_date.day and (date - current_date).days > 1:
                activity_heatmap.append(date_dic)
                current_date = date
                cnt=1
            date_dic = {
                'date': current_date,
                'amount': cnt
            }
            cnt=cnt+1
        if current_date not in activity_heatmap:
            activity_heatmap.append(date_dic)


    user_report = {
        'report_name': 'user_report',
        'user_ids': user_ids if not user_ids[0] == -1 else None,
        'open_sales_cycles': open_sales_cycles.count(),
        'closed_sales_cycles': closed_sales_cycles.count(),
        'earned_money': earned_money,
        'activity_heatmap': activity_heatmap,
        'from_date': from_date,
        'to_date': to_date}
    return user_report

def build_product_report(company_id, data={}):

    rv = {
        'report_name': 'product_report',
        'products': {},
    }
    products = Product.objects.filter(company_id=company_id)
    milestones = Milestone.objects.filter(company_id=company_id).order_by('is_system', 'sort')

    for product in products:
        '''
            {
                1: {
                    'earned_money': 500,
                    'total_cycles': 5,
                    'by_milestone': {
                        0: [], // cycles with no milestone chosen
                        1: [1,3],
                        2: [],
                        3: [4,5,6]
                    }
                }
            }
        '''
        by_milestone = {
            0: [sc.id for sc in SalesCycle.objects.filter(products__pk__in=[product.id],
                                                                milestone_id=None,
                                                                company_id=company_id,
                                                                is_global=False)]
        }

        for m in milestones:
            by_milestone[m.id] = [sc.id for sc in SalesCycle.objects.filter(products__pk__in=[product.id],
                                                                milestone_id=m.id,
                                                                company_id=company_id,
                                                                is_global=False)]
        rv['products'][product.id] = {
            'earned_money': sum(SalesCycleProductStat.objects.filter(
                                    company_id=company_id,
                                    product_id=product.id,
                                    sales_cycle__milestone__is_system=1).values_list('real_value', flat=True)),
            'total_cycles': SalesCycle.objects.filter(products__pk__in=[product.id],
                                                        company_id=company_id,
                                                        is_global=False).count(),
            'by_milestone': by_milestone,
        }




    # open_sales_cycles = SalesCycle.objects.filter(
    # 						products__in = product_ids if product_ids[0] != -1
    # 						else Product.objects.filter(company_id=company_id).values_list('id', flat=True),
    # 						milestone__is_system=0, is_global=False, date_created__range=(from_date, to_date)
    # 					)

    # closed_sales_cycles = SalesCycle.objects.filter(
    # 							products__in = product_ids if product_ids[0] != -1
    # 							else Product.objects.filter(company_id=company_id).values_list('id', flat=True),
    # 							milestone__is_system__in=[1,2],
    # 							is_global=False, date_created__range=(from_date, to_date)
    # 						)
    # successfull_cycles = closed_sales_cycles.filter(milestone__is_system=1)
    # unsuccessfull_cycles = closed_sales_cycles.filter(milestone__is_system=2)

    # earned_money = sum(SalesCycleProductStat.objects.filter(sales_cycle__in=closed_sales_cycles).values_list('real_value', flat=True))


    # if product_ids == [-1]:
    # 	products = Product.objects.filter(company_id=company_id, date_created__range=(from_date, to_date))
    # else:
    # 	products = Product.objects.filter(company_id=company_id, id__in=product_ids, date_created__range=(from_date, to_date))

    # product_stat_array = []

    # for product in products:
    # 	product_obj = {}
    # 	product_obj['id'] = product.id
    # 	obj = []
    # 	for prod_stat in product.salescycleproductstat_set.all():
    # 		obj.append({'date_edited':prod_stat.date_edited, 'real_value':prod_stat.real_value})
    # 	product_obj['object'] = obj
    # 	product_stat_array.append(product_obj)

    # product_array = []
    # for product in products:
    # 	product_obj = {}
    # 	product_obj['id'] = product.id
    # 	obj = {}
    # 	obj['open_sales_cycles'] = open_sales_cycles.filter(products__in=[product.id]).count()
    # 	obj['closed_sales_cycles'] = closed_sales_cycles.filter(products__in=[product.id]).count()
    # 	obj['successfull'] = closed_sales_cycles.filter(products__in=[product.id], milestone__is_system=1).count()
    # 	obj['unsuccessfull'] = closed_sales_cycles.filter(products__in=[product.id], milestone__is_system=2).count()
    # 	product_obj['stats'] = obj
    # 	product_array.append(product_obj)
    # user_report = {
    # 	'report_name': 'product_report',
    # 	'product_ids': product_ids if not product_ids[0] == -1 else None,
    # 	'open_sales_cycles':open_sales_cycles.count(),
    # 	'closed_sales_cycles':closed_sales_cycles.count(),
    # 	'earned_money': earned_money,
    # 	'product_stat_array':product_stat_array,
    # 	'product_array':product_array,
    # 	'successfull_cycles': successfull_cycles.count(),
    # 	'unsuccessfull_cycles': unsuccessfull_cycles.count(),
    # 	'from_date': from_date,
    # 	'to_date': to_date}
    return rv
