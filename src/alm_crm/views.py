from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from utils import reverse_lazy
from alm_user.models import User
from almanet.models import Product, Subscription
from forms import ContactForm
from models import Contact

class UserProductView(ListView):
	template_name = 'crm/dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(UserProductView, self).get_context_data(**kwargs)
		context['user'] = User.objects.get(id=self.request.user.id)
		p = Product.filter(slug=kwargs['slug'])
		u = self.request.user
		if (kwargs['slug'] != None and p):
			subscr = u.get_active_subscriptions().filter(product__slug=kwargs['slug'])
			if subscr:
				context['product'] = subscr.product
		return context

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