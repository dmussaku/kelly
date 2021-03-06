from django.contrib import admin
from django import forms
from alm_user.models import (
    User,
    Account
)
from alm_company.models import Company
from almanet.models import Service, Subscription
from alm_crm.models import Contact, Milestone


class UserAdmin(admin.ModelAdmin):
    exclude = ['last_login']

    def save_model(self, request, obj, form, change):
        obj.set_password(obj.password)
        obj.save()


class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ['organization', 'user', 'service']

    def save_model(self, request, obj, form, change):
        obj.save()
        # obj.user.connect_service(obj.service)

class ContactAdmin(admin.ModelAdmin):

	exclude = ['subscription_id']

	def save_model(self, request, obj, form, change):
		obj.save();

class MilestoneAdmin(admin.ModelAdmin):

    list_display = ['title', 'color_code']

admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(Company)
admin.site.register(Service)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Milestone, MilestoneAdmin)