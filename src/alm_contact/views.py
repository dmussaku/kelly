from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponse
from utils import reverse_lazy
from forms import ContactForm
from models import Contact

class ContactListView(ListView):
    
    model = Contact
    paginate_by = 10

class ContactCreateView(CreateView):
    form_class = ContactForm
    template_name = "contact/contact_create.html"
    success_url = reverse_lazy('contact_list')

    def form_valid(self, form):
        return super(ContactCreateView, self).form_valid(form)

class ContactUpdateView(UpdateView):
    model = Contact
    form_clas = ContactForm
    success_url = reverse_lazy('contact_list')
    template_name = "contact/contact_update.html"

class ContactDetailView(DetailView):
    model = Contact
    template_name = "contact/contact_detail.html"

def contact_export(request, pk, *args, **kwargs):
    c = Contact.objects.get(pk=pk)
    vcard = c.to_vcard().serialize()
    response = HttpResponse(vcard, mimetype='text/x-vcard')
    response['Content-Disposition'] = "attachment; filename=%s_%s.vcf" % (c.first_name, c.last_name)
    return response