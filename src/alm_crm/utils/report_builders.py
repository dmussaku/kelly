import re
from alm_crm.models import (
	SalesCycle,
	Milestone,
	Activity,
	CRMUser,
	SalesCycleProductStat
	)

def build_funnel(subscription_id):
	rv = {
		'report_name': 'funnel'
	}
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

def build_realtime_funnel(subscription_id):
	rv = {
		'report_name': 'realtime_funnel'
	}
	sales_cycles = SalesCycle.objects.filter(subscription_id=subscription_id, is_global=False)
	rv['total'] = len(sales_cycles)

	rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	
	sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len([sc for sc in sc_in_funnel if sc.milestone.id == m.id])
	return rv
		
def build_user_report(user_ids=[-1]):

	open_sales_cycles = SalesCycle.objects.filter(owner_id__in=user_ids if user_ids[0] != -1 
													else CRMUser.objects.all().values_list('id', flat=True), 
													status__in=['N', 'P'])

	closed_sales_cycles = SalesCycle.objects.filter(owner_id__in=user_ids if user_ids[0] != -1 
													else CRMUser.objects.all().values_list('id', flat=True), 
													status__in='C')
	earned_money = sum(SalesCycleProductStat.objects.filter(sales_cycle__in=closed_sales_cycles).values_list('value', flat=True))

	activity_dates = Activity.objects.filter(owner_id__in=user_ids if user_ids[0] != -1 
													else CRMUser.objects.all().values_list('id', 
														flat=True)).order_by('date_created').values_list(
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
		'user_ids': user_ids if not user_ids[0] == -1 else None,
		'open_sales_cycles': open_sales_cycles.count(),
		'closed_sales_cycles': closed_sales_cycles.count(),
		'earned_money': earned_money,
		'activity_heatmap': activity_heatmap}
	return user_report