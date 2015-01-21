from django.contrib import admin
from alm_user.models import (
	User
	)
from alm_company.models import Company
from almanet.models import Service, Subscription

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Service)
admin.site.register(Subscription)
