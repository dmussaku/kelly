from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from datetime import timedelta
from almanet.url_resolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render
from forms import ContactForm, SalesCycleForm, MentionForm, ActivityForm,\
    CommentForm, ValueForm, ActivityFeedbackForm
from models import Contact, SalesCycle, Activity, Feedback, Comment, Value


class DashboardView(TemplateView):

    def get_context_data(self, **kwargs):
        pass


class FeedView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(FeedView, self).get_context_data(**kwargs)
        user_id = self.request.user.id
        sales_cycles_data = SalesCycle.get_salescycles_by_last_activity_date(
            user_id, owned=True, mentioned=True, followed=True)
        context['sales_cycles'] = sales_cycles_data[0]
        context['sales_cycle_activities'] = sales_cycles_data[1]
        context['sales_cycle_activity_map'] = sales_cycles_data[2]
        return context


class ContactDetailView(DetailView):

    def get_object(self):
        contact_pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.get_contact_detail(contact_pk, with_vcard=True)

    def get_context_data(self, **kwargs):
        contact_pk = self.kwargs.get(self.pk_url_kwarg)
        context = super(ContactDetailView, self).get_context_data(**kwargs)
        context['activities'] = Activity.get_activities_by_contact(contact_pk)
        return context


class ContactListView(ListView):

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        user_id = self.request.user.id
        context['contacts_cold_base'] = self.model.get_cold_base()
        context['contacts_contacted_last_week'] = \
            self.model.get_contacts_for_last_activity_period(
                user_id,
                from_dt=timezone.now()-timedelta(days=7),
                to_dt=timezone.now())
        return context


# class DashBoardTemplateView(TemplateView):
#     template_name = 'crm/dashboard.html'

#     def get_context_data(self, **kwargs):
#         self.request.user
#         context = super(DashBoardTemplateView, self).get_context_data(**kwargs)
#         context['contacts'] = Contact.objects.all()[:10]
#         return context


class UserProductView(ListView):

    def get_queryset(self):
        u = self.request.user
        subscrs = u.get_active_subscriptions().filter(
            service__slug=self.kwargs['slug'])
        return subscrs




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


class ContactDeleteView(DeleteView):
    model = Contact
    success_url = reverse_lazy('contact_list')
    template_name = 'contact/contact_delete.html'


def contact_export(request, pk, format="html", locale='ru_RU', *args, **kwargs):
    c = Contact.objects.get(pk=pk)
    exported_vcard = c.export_to(format, locale=locale)
    if format == 'vcf':
        vcard = c.to_vcard()
        response = HttpResponse(vcard, mimetype='text/x-vcard')
        response['Content-Disposition'] = \
            "attachment; filename=%s_%s.vcf" % (c.name, c.pk)
        return response
    # locale = request.user.get_locale() or locale
    return render(request, 'contact/detail_vcard.html',
                  {"contact": exported_vcard})


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

    def get_context_data(self, **kwargs):
        context = super(ActivityDetailView, self).get_context_data(**kwargs)
        context['activity'] = Activity.objects.get(id=self.kwargs['pk'])
        context['comments'] = Activity.objects.get(id=self.kwargs['pk']).comments.all()
        return context

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


class ActivityFeedbackListView(ListView):
    model = Feedback
    queryset = Feedback.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super(ActivityFeedbackListView, self).get_context_data(**kwargs)
        ctx['activity_feedbacks'] = Feedback.objects.all()
        ctx['user'] = self.request.user
        return ctx


class ActivityFeedbackCreateView(CreateView):
    model = Feedback
    form_class = ActivityFeedbackForm
    template_name = "activity_feedback/activity_feedback_create.html"
    success_url = reverse_lazy('activity_feedback_list')


class ActivityFeedbackUpdateView(UpdateView):
    model = Feedback
    form_class = ActivityFeedbackForm
    template_name = "activity_feedback/activity_feedback_update.html"
    success_url = reverse_lazy('activity_feedback_list')


class ActivityFeedbackDetailView(DetailView):
    model = Feedback
    template_name = "activity_feedback/activity_feedback_detail.html"


class ActivityFeedbackDeleteView(DeleteView):
    model = Feedback
    template_name = "activity_feedback/activity_feedback_delete.html"
    success_url = reverse_lazy('activity_feedback_list')
