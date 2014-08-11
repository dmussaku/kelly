from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from utils import reverse_lazy
from forms import ContactForm
from models import Contact

class ContactListView(ListView):
    
    model = Contact
    template_name = "contact/contact_list.html"

    def get_context_data(self, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['contacts'] = Contact.objects.all()
        return context

class ContactCreateView(CreateView):
    form_class = ContactForm
    template_name = "contact/contact_create.html"
    success_url = reverse_lazy('contact_list')

class ContactUpdateView(UpdateView):
    model = Contact
    form_clas = ContactForm
    success_url = reverse_lazy('contact_list')
    template_name = "contact/contact_update.html"

    '''def get_object(self, **kwargs):
                    print kwargs
                    return Contact.objects.get(pk=kwargs['pk'])'''