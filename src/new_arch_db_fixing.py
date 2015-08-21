#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alm_crm.models import Contact, SalesCycle, Milestone, ContactList, Filter, Product, SalesCycleLogEntry
from almanet.models import Subscription
from alm_vcard.models import Tel, Email, Adr, Url
from alm_crm.models import GLOBAL_CYCLE_TITLE
from alm_user.models import User, Account
import datetime

def set_global_cycle_owner(sales_cycle):
	sales_cycle.owner = sales_cycle.contact.owner
	sales_cycle.company_id = sales_cycle.contact.company_id
	sales_cycle.save()

	return True

def set_share_data(share):
	share.share_to = share.contact.owner
	share.share_from = share.contact.owner
	share.company_id = share.contact.company_id
	share.save()

	return True

def create_milestone(type, company_id):
	if type == "SUCCESS":
		milestone = Milestone(**{'title':u'Успешно завершено', 'color_code':'#9CF4A7', 'is_system':1, 'sort':8})
		
	elif type == "FAIL":
		milestone = Milestone(**{'title':u'Не реализовано', 'color_code':'#F4A09C', 'is_system':2, 'sort':9})

	milestone.company_id = company_id
	milestone.save()

	return True

def delete_milestone(type, company_id):
	if type == "SUCCESS":
		milestones = Milestone.objects.filter(company_id=company_id, is_system=1)[1:]
	elif type == "FAIL":
		milestones = Milestone.objects.filter(company_id=company_id, is_system=2)[1:]

	for milestone in milestones:
		milestone.delete()

	return True

def set_vcard_object_type(model, model_id, _type):
	if model == "Tel":
		obj = Tel.objects.get(id=int(model_id))
		TYPE_CHOICES = [type_choice[0] for type_choice in Tel.TYPE_CHOICES]
		if _type == "":
			obj.type = Tel.TYPE_CHOICES[0][0]
		elif _type.lower() == "mobile":
			obj.type = "cell"
		else:
			for type_choice in TYPE_CHOICES:
				if _type.lower() == type_choice.lower():
					obj.type = type_choice
		obj.save()

	elif model == "Email":
		obj = Email.objects.get(id=int(model_id))
		TYPE_CHOICES = [type_choice[0] for type_choice in Email.TYPE_CHOICES]
		if _type == "":
			obj.type = Email.TYPE_CHOICES[0][0]
		else:
			for type_choice in TYPE_CHOICES:
				if _type.lower() == type_choice.lower():
					obj.type = type_choice
				else:
					obj.type = Email.TYPE_CHOICES[0][0]
		obj.save()

	elif model == "Adr":
		obj = Adr.objects.get(id=int(model_id))
		TYPE_CHOICES = [type_choice[0] for type_choice in Adr.TYPE_CHOICES]
		if _type == "":
			obj.type = Adr.TYPE_CHOICES[0][0]
		else:
			for type_choice in TYPE_CHOICES:
				if _type.lower() == type_choice.lower():
					obj.type = type_choice
		obj.save()

	elif model == "Url":
		obj = Url.objects.get(id=int(model_id))
		TYPE_CHOICES = [type_choice[0] for type_choice in Url.TYPE_CHOICES]
		if _type == "":
			obj.type = Url.TYPE_CHOICES[0][0]
		else:
			for type_choice in TYPE_CHOICES:
				if _type.lower() == type_choice.lower():
					obj.type = type_choice
		obj.save()

	return True


def main():
	with open('check_db.log') as f:
		lines = f.readlines()

	for line in lines:
		warning_fixed = False
		if u'DIFFERENT_COMPANY_IDS' in line or u'DIFFERENT_OWNERS' in line:
			model_name = line.split('{')[1].split('}')[0]
			model_id = line.split('{')[2].split('}')[0]

			if model_name == u"SalesCycle":
				sc = SalesCycle.objects.get(id=int(model_id))

				if sc.title == GLOBAL_CYCLE_TITLE:
					warning_fixed = set_global_cycle_owner(sc)

			elif model_name == u"Share":
				share = Share.objects.get(id=int(model_id))

				if share.share_from == share.share_to:
					correct_contact = True

					for sc in share.contact.sales_cycles.all():
						if sc.company_id != share.contact.company_id:
							correct_contact = False

					if correct_contact:
						warning_fixed = set_share_data(share)
			elif model_name == u"Product":
				product = Product.objects.get(id=int(model_id))
				obj_comp_id_equal_user_comp_id = True
				for sc in product.sales_cycles.all():
					if sc.company_id != product.owner.accounts.first().company_id:
						obj_comp_id_equal_user_comp_id = False

				if obj_comp_id_equal_user_comp_id:
					product.company_id = product.owner.accounts.first().company_id

				product.save()

			elif model_name == u"SalesCycleLogEntry":
				scle = SalesCycleLogEntry.objects.get(id = int(model_id))

				if scle.company_id == None:
					scle.company_id = scle.owner.accounts.first().company_id
					warning_fixed = True

				scle.save()

			elif model_name == u"ContactList":
				contact_list = ContactList.objects.get(id=int(model_id))
				if contact_list.contacts.count() == 0:
					contact_list.company_id = contact_list.owner.accounts.first().company_id
					warning_fixed = True
				else:
					contain_user_contacts = True
					for contact in contact_list.contacts.all():
						if contact not in contact_list.owner.owned_contacts.all():
							contain_user_contacts = False

					if contain_user_contacts:
						contact_list.company_id = contact_list.owner.accounts.first().company_id
						warning_fixed = True

				contact_list.save()

			elif model_name == u"Filter":
				_filter = Filter.objects.get(id=int(model_id))
				_filter.company_id = _filter.owner.accounts.first().company_id
				_filter.save()
				warning_fixed = True


		elif u'ILLEGAL_AMOUNT_OF_MILESTONES' in line:
			model_id = line.split('{')[2].split('}')[0]
			milestone_type = line.split('{')[3].split('}')[0]
			amount = line.split('{')[4].split('}')[0]

			if int(amount) == 0:
				warning_fixed = create_milestone(type = milestone_type, company_id = model_id)

			elif int(amount) > 0:
				warning_fixed = delete_milestone(type = milestone_type, company_id = model_id)

		elif u'ILLEGAL_TYPE' in line:
			model_name = line.split('{')[1].split('}')[0]
			model_id = line.split('{')[2].split('}')[0]
			_type = line.split('{')[3].split('}')[0]

			warning_fixed = set_vcard_object_type(model = model_name, model_id = model_id, _type = _type)

		if not warning_fixed:
			with open("check_db.log", "a") as _file:
				if u"CHECK DATABASE STARTED" in line:
					_file.write(u"=================================================================\n")
					_file.write(u"INFO:root:%s CORRECTING DATABASE STARTED"%datetime.datetime.now())
				elif u"CHECK DATABASE FINISHED" in line:
					_file.write(u"INFO:root:%s CHECK DATABASE FINISHED"%datetime.datetime.now())
				else:
					_file.write(line)
					
main()

