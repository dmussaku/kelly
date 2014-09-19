from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from almanet.url_resolvers import reverse_lazy
from models import *
from forms import *
import string
import os
import random
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper

def filename_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def import_vcard(request):
    pass

def export_vcard(request, id):
    try:
        vcard = VCard.objects.get(id=id)
    except VCard.DoesNotExist:
        return HttpResponse("Object doesn't exist")
    temp = NamedTemporaryFile()
    response = HttpResponse(FileWrapper(temp), mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s.txt"' % 'vcard'
    response.write(vcard.exportTo('vCard'))
    return response



class VCardListView(ListView):
    model = VCard
    template_name = 'vcard/vcard_list.html'


class VCardCreateView(CreateView):
    form_class = VCardForm
    template_name = 'vcard/vcard_create.html'


class TelCreateView(CreateView):
    form_class = TelForm
    template_name = 'vcard/tel_create.html'


class EmailCreateView(CreateView):
    form_class = EmailForm 
    template_name = 'vcard/email_create.html'


class GeoCreateView(CreateView):
    form_class = GeoForm
    template_name = 'vcard/geo_create.html'


class OrgCreateView(CreateView):
    form_class = OrgForm
    template_name = 'vcard/org_create.html'


class AdrCreateView(CreateView):
    form_class = AdrForm
    template_name = 'vcard/adr_create.html'


class AgentCreateView(CreateView):
    form_class = AgentForm
    template_name = 'vcard/agent_create.html'


class CategoryCreateView(CreateView):
    form_class = CategoryForm
    template_name = 'vcard/category_create.html'


class KeyCreateView(CreateView):
    form_class = KeyForm
    template_name = 'vcard/key_create.html'


class LabelCreateView(CreateView):
    form_class = LabelForm
    template_name = 'vcard/label_create.html'


class MailerCreateView(CreateView):
    form_class = MailerForm
    template_name = 'vcard/mailer_create.html'


class NicknameCreateView(CreateView):
    form_class = NicknameForm
    template_name = 'vcard/nickname_create.html'


class NoteCreateView(CreateView):
    form_class = NoteForm
    template_name = 'vcard/note_create.html'


class RoleCreateView(CreateView):
    form_class = RoleForm
    template_name = 'vcard/role_create.html'


class TitleCreateView(CreateView):
    form_class = TitleForm
    template_name = 'vcard/title_create.html'


class TzCreateView(CreateView):
    form_class = TzForm
    template_name = 'vcard/tz_create.html'


class UrlCreateView(CreateView):
    form_class = UrlForm
    template_name = 'vcard/url_create.html'


class VCardUpdateView(UpdateView):
    model = VCard
    form_class = VCardForm
    template_name = 'vcard/vcard_create.html'


class TelUpdateView(UpdateView):
    model = Tel
    form_class = TelForm
    template_name = 'vcard/tel_create.html'


class EmailUpdateView(UpdateView):
    model = Email
    form_class = EmailForm
    template_name = 'vcard/email_create.html'


class GeoUpdateView(UpdateView):
    model = Geo
    form_class = GeoForm
    template_name = 'vcard/geo_create.html'


class OrgUpdateView(UpdateView):
    model = Org
    form_class = OrgForm
    template_name = 'vcard/org_create.html'


class AdrUpdateView(UpdateView):
    model = Adr
    form_class = AdrForm
    template_name = 'vcard/adr_create.html'


class AgentUpdateView(UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'vcard/agent_create.html'


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'vcard/category_create.html'


class KeyUpdateView(UpdateView):
    model = Key
    form_class = KeyForm
    template_name = 'vcard/key_create.html'


class LabelUpdateView(UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'vcard/label_create.html'


class MailerUpdateView(UpdateView):
    model = Mailer
    form_class = MailerForm
    template_name = 'vcard/mailer_create.html'


class NicknameUpdateView(UpdateView):
    model = Nickname
    form_class = NicknameForm
    template_name = 'vcard/nickname_create.html'


class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'vcard/note_create.html'


class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'vcard/role_create.html'


class TitleUpdateView(UpdateView):
    model = Title
    form_class = TitleForm
    template_name = 'vcard/title_create.html'


class TzUpdateView(UpdateView):
    model = Tz
    form_class = TzForm
    template_name = 'vcard/tz_create.html'


class UrlUpdateView(UpdateView):
    model = Url
    form_class = UrlForm
    template_name = 'vcard/url_create.html'
