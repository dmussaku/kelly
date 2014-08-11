from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from utils import reverse_lazy
from forms import ContactForm
from models import Contact

class ContactListView(ListView):
    
    model = Contact
    template_name = "contact/contact_list.html"


class ContactCreateView(CreateView):
    form_class = ContactForm
    template_name = "contact/contact_create.html"
    success_url = reverse_lazy('contact_list')

class ContactUpdateView(UpdateView):
    model = Contact
    form_clas = ContactForm
    success_url = reverse_lazy('contact_list')
    template_name = "contact/contact_update.html"

class ContactDetailView(DetailView):
    model = Contact
    template_name = "contact/contact_detail.html"