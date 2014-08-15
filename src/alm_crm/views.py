from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from utils import reverse_lazy
from alm_user.models import User
from almanet.models import Product, Subscription
from forms import ContactForm, GoalForm
from models import Contact, Goal

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


class ContactDeleteView(DeleteView):
    model = Contact
    success_url = reverse_lazy('contact_list')
    template_name = 'contact/contact_delete.html'


class GoalListView(ListView):
    
    model = Goal
    paginate_by = 10


class GoalCreateView(CreateView):
    form_class = GoalForm
    template_name = "goal/goal_create.html"
    success_url = reverse_lazy('goal_list')

    def form_valid(self, form):
        return super(GoalCreateView, self).form_valid(form)


class GoalUpdateView(UpdateView):
    model = Goal
    form_clas = GoalForm
    success_url = reverse_lazy('goal_list')
    template_name = "goal/goal_update.html"


class GoalDetailView(DetailView):
    model = Goal
    template_name = "goal/goal_detail.html"


class GoalDeleteView(DeleteView):
    model = Goal
    success_url = reverse_lazy('goal_list')
    template_name = 'goal/goal_delete.html'    