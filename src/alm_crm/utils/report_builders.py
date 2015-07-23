import re
from alm_crm.models import (
	SalesCycle,
	Milestone,
	Activity,
	CRMUser,
	SalesCycleProductStat,
	Product,
	ProductGroup,
	SalesCycleLogEntry,
	Milestone
	)
from datetime import datetime
from django.utils import timezone
import pytz

def build_funnel(subscription_id, product_ids=[]):
	rv = {
		'report_name': 'funnel'
	}
	if product_ids:
		sales_cycles = SalesCycle.objects.filter(
			subscription_id=subscription_id, 
			products__in=product_ids, 
			is_global=False)
	else:
		sales_cycles = SalesCycle.objects.filter(subscription_id=subscription_id, is_global=False)
	rv['total'] = len(sales_cycles)

	rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	
	sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len(sc_in_funnel)
		sc_in_funnel = [sc for sc in sc_in_funnel if sc.milestone.id != m.id]
	return rv

def build_realtime_funnel(subscription_id, product_ids=[]):
	rv = {
		'report_name': 'realtime_funnel'
	}
	if product_ids:
		sales_cycles = SalesCycle.objects.filter(
			subscription_id=subscription_id, 
			products__in=product_ids, 
			is_global=False)
	else:
		sales_cycles = SalesCycle.objects.filter(subscription_id=subscription_id, is_global=False)
	rv['total'] = len(sales_cycles)

	rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	
	sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len([sc for sc in sc_in_funnel if sc.milestone.id == m.id])
	return rv
		
def build_user_report(subscription_id, user_ids=[-1], from_date=None, to_date=None):
	if from_date == None:
		from_date = datetime(2014, 1, 1).replace(tzinfo=pytz.UTC)

	if to_date == None:
		to_date = datetime.now().replace(tzinfo=pytz.UTC)

	open_sales_cycles = SalesCycle.objects.filter(owner_id__in=user_ids if user_ids[0] != -1 
													else CRMUser.objects.filter(subscription_id=subscription_id).values_list('id', flat=True), 
													status__in=['N', 'P'],
													date_created__range=(from_date, to_date), is_global=False)
	close_activities = Activity.objects.filter(owner_id__in=user_ids, description__startswith='Closed')
	closed_sales_cycles = SalesCycle.objects.filter(status__in='C', rel_activities__in=close_activities, date_created__range=(from_date, to_date), is_global=False)
	earned_money = sum(SalesCycleProductStat.objects.filter(sales_cycle__in=closed_sales_cycles).values_list('value', flat=True))

	activity_dates = Activity.objects.filter(owner_id__in=user_ids if user_ids[0] != -1 
													else CRMUser.objects.filter(subscription_id=subscription_id).values_list('id', 
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

def build_product_report(subscription_id, product_ids=[-1], from_date=None, to_date=None):
	if from_date == None:
		from_date = datetime(2014, 1, 1).replace(tzinfo=pytz.UTC)

	if to_date == None:
		to_date = datetime.now().replace(tzinfo=pytz.UTC)

	products_amount = len(product_ids) if len(product_ids) > 1 else Product.objects.filter(subscription_id=subscription_id).count()
	open_sales_cycles = SalesCycle.objects.filter(
							products__in = product_ids if product_ids[0] != -1 
							else Product.objects.filter(subscription_id=subscription_id).values_list('id', flat=True),
							status__in=['N', 'P'], is_global=False, date_created__range=(from_date, to_date)
						).count()

	closed_sales_cycles = SalesCycle.objects.filter(
								products__in = product_ids if product_ids[0] != -1 
								else Product.objects.filter(subscription_id=subscription_id).values_list('id', flat=True),
								status='C',
								is_global=False, date_created__range=(from_date, to_date)
							)
	earned_money = sum(SalesCycleProductStat.objects.filter(sales_cycle__in=closed_sales_cycles).values_list('value', flat=True))

	user_report = {
		'report_name': 'product_report',
		'product_ids': product_ids if not product_ids[0] == -1 else None,
		'products_amount': products_amount,
		'open_sales_cycles':open_sales_cycles,
		'closed_sales_cycles':closed_sales_cycles.count(),
		'earned_money': earned_money,
		'from_date': from_date,
		'to_date': to_date}
	return user_report