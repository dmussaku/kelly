from .models import *

from .admin_views import *
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf.urls import *
from django.utils.translation import ugettext as _


class TelInline(admin.StackedInline):
    model = Tel
    extra = 1


class EmailInline(admin.StackedInline):
    model = Email
    extra = 1


class AdrInline(admin.StackedInline):
    model = Adr
    extra = 1


class GeoInline(admin.StackedInline):
    model = Geo
    extra = 1


class AgentInline(admin.StackedInline):
    model = Agent
    extra = 1


class CategoryInline(admin.StackedInline):
    model = Category
    extra = 1


class KeyInline(admin.StackedInline):
    model = Key
    extra = 1


class LabelInline(admin.StackedInline):
    model = Label
    extra = 1


# class LogoInline(admin.StackedInline):
#    model = Logo
#    extra = 1


class MailerInline(admin.StackedInline):
    model = Mailer
    extra = 1


class NicknameInline(admin.StackedInline):
    model = Nickname
    extra = 1


class NoteInline(admin.StackedInline):
    model = Note
    extra = 1


# class PhotoInline(admin.StackedInline):
#    model = vcard.models.Photo
#    extra = 1


class RoleInline(admin.StackedInline):
    model = Role
    extra = 1


# class SoundInline(admin.StackedInline):
#    model = Sound
#    extra = 1


class TitleInline(admin.StackedInline):
    model = Title
    extra = 1


class TzInline(admin.StackedInline):
    model = Tz
    extra = 1


class UrlInline(admin.StackedInline):
    model = Url
    extra = 1


def to_vcf_file(modeladmin, request, queryset):
    return vcf_file_view(request, queryset)
to_vcf_file.short_description = "Create vcf file with marked objects"


class VCardAdmin(admin.ModelAdmin):
    actions = [to_vcf_file]
    # list_display = ('selectVCFLink')
    fields = ['fn', 'family_name', 'given_name', 'additional_name', 'honorific_prefix', 'honorific_suffix', 'bday', 'classP']
    inlines = [TelInline, EmailInline, AdrInline, TitleInline, AgentInline, CategoryInline, KeyInline, NicknameInline, MailerInline, NoteInline, RoleInline, TzInline, UrlInline, GeoInline]

    def get_urls(self):
        urls = super(VCardAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^selectVCF/confirmVCF/uploadVCF/$', self.admin_site.admin_view(self.uploadVCF)),
            (r'^selectVCF/confirmVCF/$', self.admin_site.admin_view(self.confirmVCF)),
            (r'^selectVCF/$', self.admin_site.admin_view(self.selectVCF))
        )
        return my_urls + urls

    def uploadVCF(self, request):
        """ TODO: Docstring """
        if 'confirm' not in request.REQUEST:
            return HttpResponseRedirect('/admin/vcard/contact')

        newContactList = request.session['unconfirmedContacts']

        for i in newContactList :

            i.commit()

        return HttpResponseRedirect('/admin/vcard/contact')

    def confirmVCF(self, request):
        newContactList = []

        if 'upfile' not in request.FILES:
            return HttpResponseRedirect('/admin/vcard/contact/selectVCF/')

        try:
            for o in vobject.readComponents(request.FILES['upfile']):
                vc = VCard.importFrom("vObject", o)
                newContactList.append(vc)

        except Exception as e:
            for i in newContactList:
                i.delete()

            return render_to_response('admin/errorVCF.html', {'exception': e}, context_instance=RequestContext(request))

        request.session['unconfirmedContacts'] = newContactList

        errorCount = 0

        for i in newContactList:
            if len(i.errorList) > 0:
                errorCount += 1

        return render_to_response('admin/confirmVCF.html', {'contactSet': newContactList, 'errorCount': errorCount}, context_instance=RequestContext(request))

    def selectVCFLink(self):
        """ TODO: Docstring """

        return '<a href="../newsletter/%s/">%s</a>' % (obj.newsletter.id, obj.newsletter)
    selectVCFLink.short_description = _('Select VCF')
    selectVCFLink.allow_tags = True

    def selectVCF(self, request):
        """ TODO: Docstring """
        return render_to_response('admin/selectVCF.html', context_instance=RequestContext(request))


admin.site.register(VCard, VCardAdmin)
