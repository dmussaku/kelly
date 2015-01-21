from django.contrib import admin
from alm_user.models import (
	User
	)
from alm_company.models import Company
from almanet.models import Service, Subscription

class UserAdmin(admin.ModelAdmin):
	exclude = ['last_login']
	def save_model(self, request, obj, form, change):
		obj.set_password(obj.password)
		obj.save()

class SubscriptionAdmin(admin.ModelAdmin):
	list_display = ['organization', 'user', 'service']
	def save_model(self, request, obj, form, change):
		obj.save()
		obj.user.connect_service(obj.service)

admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Service)
admin.site.register(Subscription, SubscriptionAdmin)

