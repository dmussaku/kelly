#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from almanet.models import Plan

class Command(BaseCommand):

	def handle(self, *args, **options):
		plan1 = Plan(
			name_ru = 'Стартовый план',
		    description_ru = '',
		    name_en = 'Starters plan',
		    description_en = '',
		    price_kzt = 5000,
		    price_usd = 25,
		    users_num = 10,
		    contacts_num = 100,
		    space_per_user = 1,
		    pic = 'common-files/icons/retina-ready-s@2x.png'
			)
		plan2 = Plan(
			name_ru = 'Средний бизнесс',
		    description_ru = '',
		    name_en = 'Medium business',
		    description_en = '',
		    price_kzt = 10000,
		    price_usd = 50,
		    users_num = 20,
		    contacts_num = 2000,
		    space_per_user = 5,
		    pic = 'common-files/icons/rocket@2x.png'
			)
		plan3 = Plan(
			name_ru = 'Крупный бизнесс',
		    description_ru = '',
		    name_en = 'Corporate business',
		    description_en = '',
		    price_kzt = 20000,
		    price_usd = 100,
		    users_num = 0,
		    contacts_num = 0,
		    space_per_user = 10,
		    pic = 'common-files/icons/magic-wand@2x.png'
			)
		plan1.save()
		print "%s has been saved" % plan1
		plan2.save()
		print "%s has been saved" % plan1
		plan3.save()
		print "%s has been saved" % plan1

