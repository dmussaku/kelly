from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from almanet.url_resolvers import reverse_lazy, reverse
from models import *
from alm_crm.models import Contact
from forms import *
import string
import os
import random
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper
import json


def filename_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def import_vcard(request, **kwargs):
    '''
    In this view i prompt the user to upload the vcard which can have either one
    vcard or multiple vcard information. Then i split the input to data_list list
    and create vcard objects for every vcard parsed in data_list
    '''
    if request.method == 'POST':
        form = VCardUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_list = request.FILES['myfile'].read().split('END:VCARD')[:-1]
            contact_ids=[]
            for i in range(0, len(data_list)):
                data_list[i] += 'END:VCARD'
                c = Contact.upload_contacts('vcard', data_list[i], save=True)
                contact_ids.append({'contact_id':c.id, 'name':c.name})
                #contact_ids.append(Contact.upload_contacts('vcard', data_list[i], save=True).id)
            return HttpResponse(json.dumps(contact_ids), content_type='application/json')
    else:
        form = VCardUploadForm()
    return render_to_response('vcard/vcard_upload.html',
                                {'form':form},
                                context_instance=RequestContext(request)
                                )
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
    paginate_by = 20


class VCardDetailView(DetailView):

    model = VCard
    template_name = 'vcard/vcard_detail.html'

    def get_context_data(self, **kwargs):
        context = super(VCardDetailView, self).get_context_data(**kwargs)
        vcard_id = self.kwargs['pk']
        context['vcard'] = VCard.objects.get(id=vcard_id)
        context['tels'] = Tel.objects.filter(vcard_id=vcard_id)
        context['emails'] = Email.objects.filter(vcard_id=vcard_id)
        context['geos'] = Geo.objects.filter(vcard_id=vcard_id)
        context['orgs'] = Org.objects.filter(vcard_id=vcard_id)
        context['adrs'] = Adr.objects.filter(vcard_id=vcard_id)
        context['agents'] = Agent.objects.filter(vcard_id=vcard_id)
        context['categories'] = Category.objects.filter(vcard_id=vcard_id)
        context['keys'] = Key.objects.filter(vcard_id=vcard_id)
        context['labels'] = Label.objects.filter(vcard_id=vcard_id)
        context['mailers'] = Mailer.objects.filter(vcard_id=vcard_id)
        context['nicknames'] = Nickname.objects.filter(vcard_id=vcard_id)
        context['notes'] = Note.objects.filter(vcard_id=vcard_id)
        context['roles'] = Role.objects.filter(vcard_id=vcard_id)
        context['titles'] = Title.objects.filter(vcard_id=vcard_id)
        context['tzs'] = Tz.objects.filter(vcard_id=vcard_id)
        context['urls'] = Url.objects.filter(vcard_id=vcard_id)
        return context

class InitialCreateView(CreateView):

    def get_form_kwargs(self, **kwargs):
        self.initial = {'vcard':self.kwargs['pk']}
        return super(InitialCreateView, self).get_form_kwargs(**kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy('vcard_detail', kwargs= {'pk':self.kwargs['pk']})

class InitialUpdateView(UpdateView):

    def get_success_url(self, **kwrags):
        return reverse_lazy('vcard_detail', kwargs= {'pk':self.kwargs['pk']})


class VCardCreateView(CreateView):
    form_class = VCardForm
    template_name = 'vcard/vcard_create.html'



class TelCreateView(InitialCreateView):
    form_class = TelForm
    template_name = 'vcard/tel_create.html'

    def get_success_url(self, **kwargs):
        return super(TelCreateView, self).get_success_url(**kwargs)


class EmailCreateView(InitialCreateView):
    form_class = EmailForm
    template_name = 'vcard/email_create.html'

    def get_success_url(self, **kwargs):
        return super(EmailCreateView, self).get_success_url(**kwargs)

class GeoCreateView(InitialCreateView):
    form_class = GeoForm
    template_name = 'vcard/geo_create.html'

    def get_success_url(self, **kwargs):
        return super(GeoCreateView, self).get_success_url(**kwargs)


class OrgCreateView(InitialCreateView):
    form_class = OrgForm
    template_name = 'vcard/org_create.html'

    def get_success_url(self, **kwargs):
        return super(OrgCreateView, self).get_success_url(**kwargs)

class AdrCreateView(InitialCreateView):
    form_class = AdrForm
    template_name = 'vcard/adr_create.html'

    def get_success_url(self, **kwargs):
        return super(AdrCreateView, self).get_success_url(**kwargs)


class AgentCreateView(InitialCreateView):
    form_class = AgentForm
    template_name = 'vcard/agent_create.html'

    def get_success_url(self, **kwargs):
        return super(AgentCreateView, self).get_success_url(**kwargs)


class CategoryCreateView(InitialCreateView):
    form_class = CategoryForm
    template_name = 'vcard/category_create.html'

    def get_success_url(self, **kwargs):
        return super(CategoryCreateView, self).get_success_url(**kwargs)


class KeyCreateView(InitialCreateView):
    form_class = KeyForm
    template_name = 'vcard/key_create.html'

    def get_success_url(self, **kwargs):
        return super(KeyCreateView, self).get_success_url(**kwargs)


class LabelCreateView(InitialCreateView):
    form_class = LabelForm
    template_name = 'vcard/label_create.html'

    def get_success_url(self, **kwargs):
        return super(LabelCreateView, self).get_success_url(**kwargs)


class MailerCreateView(InitialCreateView):
    form_class = MailerForm
    template_name = 'vcard/mailer_create.html'

    def get_success_url(self, **kwargs):
        return super(MailerCreateView, self).get_success_url(**kwargs)


class NicknameCreateView(InitialCreateView):
    form_class = NicknameForm
    template_name = 'vcard/nickname_create.html'

    def get_success_url(self, **kwargs):
        return super(NicknameCreateView, self).get_success_url(**kwargs)


class NoteCreateView(InitialCreateView):
    form_class = NoteForm
    template_name = 'vcard/note_create.html'

    def get_success_url(self, **kwargs):
        return super(NoteCreateView, self).get_success_url(**kwargs)


class RoleCreateView(InitialCreateView):
    form_class = RoleForm
    template_name = 'vcard/role_create.html'

    def get_success_url(self, **kwargs):
        return super(RoleCreateView, self).get_success_url(**kwargs)


class TitleCreateView(InitialCreateView):
    form_class = TitleForm
    template_name = 'vcard/title_create.html'

    def get_success_url(self, **kwargs):
        return super(TitleCreateView, self).get_success_url(**kwargs)


class TzCreateView(InitialCreateView):
    form_class = TzForm
    template_name = 'vcard/tz_create.html'

    def get_success_url(self, **kwargs):
        return super(TzCreateView, self).get_success_url(**kwargs)


class UrlCreateView(InitialCreateView):
    form_class = UrlForm
    template_name = 'vcard/url_create.html'

    def get_success_url(self, **kwargs):
        return super(UrlCreateView, self).get_success_url(**kwargs)


class VCardUpdateView(UpdateView):
    model = VCard
    form_class = VCardForm
    template_name = 'vcard/vcard_create.html'


class TelUpdateView(InitialUpdateView):
    model = Tel
    form_class = TelForm
    template_name = 'vcard/tel_create.html'

    def get_object(self, **kwargs):
        return Tel.objects.get(id=self.kwargs['id'])

    def get_success_url(self, **kwargs):
        self.kwargs['pk'] = VCard.objects.get(id=Tel.objects.get(id=self.kwargs['id']).vcard_id).id
        return super(TelUpdateView, self).get_success_url(**kwargs)


class EmailUpdateView(InitialUpdateView):
    model = Email
    form_class = EmailForm
    template_name = 'vcard/email_create.html'

    def get_object(self, **kwargs):
        return Email.objects.get(id=self.kwargs['id'])

    def get_success_url(self, **kwargs):
        self.kwargs['pk'] = VCard.objects.get(id=Email.objects.get(id=self.kwargs['id']).vcard_id).id
        return super(EmailUpdateView, self).get_success_url(**kwargs)


class GeoUpdateView(UpdateView):
    model = Geo
    form_class = GeoForm
    template_name = 'vcard/geo_create.html'

    def get_object(self, **kwargs):
        return Geo.objects.get(id=self.kwargs['id'])

    def get_success_url(self, **kwargs):
        self.kwargs['pk'] = VCard.objects.get(id=Geo.objects.get(id=self.kwargs['id']).vcard_id).id
        return super(GeoUpdateView, self).get_success_url(**kwargs)


class OrgUpdateView(UpdateView):
    model = Org
    form_class = OrgForm
    template_name = 'vcard/org_create.html'

    def get_object(self, **kwargs):
        return Org.objects.get(id=self.kwargs['id'])


class AdrUpdateView(UpdateView):
    model = Adr
    form_class = AdrForm
    template_name = 'vcard/adr_create.html'

    def get_object(self, **kwargs):
        return Adr.objects.get(id=self.kwargs['id'])


class AgentUpdateView(UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'vcard/agent_create.html'

    def get_object(self, **kwargs):
        return Agent.objects.get(id=self.kwargs['id'])


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'vcard/category_create.html'

    def get_object(self, **kwargs):
        return Category.objects.get(id=self.kwargs['id'])


class KeyUpdateView(UpdateView):
    model = Key
    form_class = KeyForm
    template_name = 'vcard/key_create.html'

    def get_object(self, **kwargs):
        return Key.objects.get(id=self.kwargs['id'])


class LabelUpdateView(UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'vcard/label_create.html'

    def get_object(self, **kwargs):
        return Label.objects.get(id=self.kwargs['id'])


class MailerUpdateView(UpdateView):
    model = Mailer
    form_class = MailerForm
    template_name = 'vcard/mailer_create.html'

    def get_object(self, **kwargs):
        return Mailer.objects.get(id=self.kwargs['id'])


class NicknameUpdateView(UpdateView):
    model = Nickname
    form_class = NicknameForm
    template_name = 'vcard/nickname_create.html'

    def get_object(self, **kwargs):
        return Nickname.objects.get(id=self.kwargs['id'])


class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'vcard/note_create.html'

    def get_object(self, **kwargs):
        return Note.objects.get(id=self.kwargs['id'])


class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'vcard/role_create.html'

    def get_object(self, **kwargs):
        return Role.objects.get(id=self.kwargs['id'])


class TitleUpdateView(UpdateView):
    model = Title
    form_class = TitleForm
    template_name = 'vcard/title_create.html'

    def get_object(self, **kwargs):
        return Title.objects.get(id=self.kwargs['id'])


class TzUpdateView(UpdateView):
    model = Tz
    form_class = TzForm
    template_name = 'vcard/tz_create.html'

    def get_object(self, **kwargs):
        return Tz.objects.get(id=self.kwargs['id'])


class UrlUpdateView(UpdateView):
    model = Url
    form_class = UrlForm
    template_name = 'vcard/url_create.html'

    def get_object(self, **kwargs):
        return Url.objects.get(id=self.kwargs['id'])
