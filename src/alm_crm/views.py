from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from almanet.url_resolvers import reverse_lazy
from alm_user.models import User
from django.http import HttpResponse
from django.shortcuts import render
from almanet.models import Product, Subscription
from forms import ContactForm, SalesCycleForm, MentionForm, ActivityForm, CommentForm, ValueForm
from models import Contact, SalesCycle, Activity, Mention, Comment, Value


class UserProductView(ListView):
    template_name = 'crm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(UserProductView, self).get_context_data(**kwargs)
        context['user'] = User.objects.get(id=self.request.user.id)
        p = Product.filter(slug=kwargs['slug'])
        u = self.request.user
        if (kwargs['slug'] != None and p):
            subscr = u.get_active_subscriptions().filter(
                product__slug=kwargs['slug'])
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


class ContactAddMentionView(UpdateView):
    model = Contact
    form_class = MentionForm #context_type, context_id
    success_url = reverse_lazy('contact_list')
    template_name = "contact/contact_add_mention.html"

    def post(self, request, *args, **kwargs):
        self.model.objects.get(id=self.kwargs['pk']).add_mention(list(request.POST['user_id']))
        return super(ContactAddMentionView, self).post(request, *args, **kwargs)


class ContactDetailView(DetailView):
    model = Contact
    template_name = "contact/contact_detail.html"


class ContactDeleteView(DeleteView):
    model = Contact
    success_url = reverse_lazy('contact_list')
    template_name = 'contact/contact_delete.html'


def contact_export(request, pk, format="web", locale='ru_RU', *args, **kwargs):
    c = Contact.objects.get(pk=pk)
    if format == 'vcf':
        vcard = c.to_vcard().serialize()
        response = HttpResponse(vcard, mimetype='text/x-vcard')
        response[
            'Content-Disposition'] = "attachment; filename=%s_%s.vcf" % (c.first_name, c.last_name)
        return response
    # locale = request.user.get_locale() or locale
    return render(request, 'contact/vcards/vcard.%s.html' % (locale), {"contact": c})


class SalesCycleListView(ListView):
    model = SalesCycle
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(SalesCycleListView, self).get_context_data(**kwargs)
        context['form'] = MentionForm
        return context


class SalesCycleCreateView(CreateView):
    form_class = SalesCycleForm
    template_name = "sales_cycle/sales_cycle_create.html"
    success_url = reverse_lazy('sales_cycle_list')


class SalesCycleUpdateView(UpdateView):
    model = SalesCycle
    form_class = SalesCycleForm
    success_url = reverse_lazy('sales_cycle_list')
    template_name = "sales_cycle/sales_cycle_update.html"

class SalesCycleAddMentionView(UpdateView):
    model = SalesCycle
    form_class = MentionForm #context_type, context_id
    success_url = reverse_lazy('sales_cycle_list')
    template_name = "sales_cycle/sales_cycle_add_mention.html"

    def post(self, request, *args, **kwargs):
        self.model.objects.get(id=self.kwargs['pk']).add_mention(list(request.POST['user_id']))
        return super(SalesCycleAddMentionView, self).post(request, *args, **kwargs)


class SalesCycleDetailView(DetailView):
    model = SalesCycle
    template_name = "sales_cycle/sales_cycle_detail.html"

    def get_context_data(self, **kwargs):
        context = super(SalesCycleDetailView, self).get_context_data(**kwargs)
        print SalesCycle.objects.get(id=self.kwargs['pk'])
        context['sales_cycle'] = SalesCycle.objects.get(id=self.kwargs['pk'])
        return context

class SalesCycleDeleteView(DeleteView):
    model = SalesCycle
    success_url = reverse_lazy('sales_cycle_list')
    template_name = 'sales_cycle/sales_cycle_delete.html'


class ActivityCreateView(CreateView):
    model = Activity 
    form_class = ActivityForm
    template_name = 'activity/activity_create.html'
    success_url = reverse_lazy('activity_list')



class ActivityListView(ListView):
    model = Activity
    template_name = 'activity/activity_list.html'

    def get_context_data(self, **kwargs):
        context = super(ActivityListView, self).get_context_data(**kwargs)
        context['activities'] = Activity.objects.all()
        return context

 
class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'activity/activity_detail.html'


class ActivityUpdateView(UpdateView):
    model = Activity
    template_name = 'activity/activity_update.html'

    def get_success_url(self):
        return reverse_lazy('activity_detail', kwargs={'pk': self.kwargs['pk']})


class ActivityDeleteView(DeleteView):
    model = Activity
    success_url = reverse_lazy('activity_list')
    template_name = 'activity/activity_delete.html'


class CommentListView(ListView):
    model = Comment
    template_name = 'comment/comment_list.html'


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('comment_list')
    template_name = 'comment/comment_create.html'
    '''
    def get_initial(self):
       return {'author' : self.request.user}
    '''

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.date_edited = timezone.now()
        return super(CommentCreateView, self).form_valid(form)
        

class CommentAddMentionView(CreateView):
    model = Comment
    form_class = MentionForm #context_type, context_id
    success_url = reverse_lazy('comment_list')
    template_name = "comment/comment_add_mention.html"

    def post(self, request, *args, **kwargs):
        self.model.objects.get(id=self.kwargs['pk']).add_mention(list(request.POST['user_id']))
        return super(CommentAddMentionView, self).post(request, *args, **kwargs)


class ValueListView(ListView):

    model = Value
    queryset = Value.objects.all()


    def get_context_data(self, **kwargs):
        ctx = super(ValueListView, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx


class ValueCreateView(CreateView):
    form_class = ValueForm
    template_name = "value/value_create.html"
    success_url = reverse_lazy('value_list')


class ValueUpdateView(UpdateView):
    model = Value
    form_class = ValueForm
    template_name = "value/value_update.html"
    success_url = reverse_lazy('value_list')


class ValueDetailView(DetailView):
    model = Value
    template_name = "value/value_detail.html"


class ValueDeleteView(DeleteView):
    model = Value
    template_name = "value/value_delete.html"
    success_url = reverse_lazy('value_list')