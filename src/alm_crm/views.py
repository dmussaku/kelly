import json
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.http import HttpResponseRedirect
from datetime import timedelta
from almanet.url_resolvers import reverse_lazy, reverse as almanet_reverse
from django.http import HttpResponse
from django.shortcuts import render
from forms import ContactForm, SalesCycleForm, MentionForm, ActivityForm,\
    CommentForm, ValueForm, ActivityFeedbackForm, ShareForm
from models import Contact, SalesCycle, Activity, Feedback, Comment, Value,\
    CRMUser
from alm_vcard.forms import VCardUploadForm
from django.views.generic.base import View


class DashboardView(View):

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['form'] = VCardUploadForm
        context['subdomain'] = self.request.subdomain
        return context

    def get(self, request, *a, **kw):
        url = almanet_reverse('feed', kwargs={'slug': self.kwargs.get('slug')},
                              subdomain=request.user_env['subdomain'])
        return HttpResponseRedirect(url)


class FeedView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(FeedView, self).get_context_data(**kwargs)
        crmuser_id = self.request.user.get_crmuser().id
        sales_cycles_data = SalesCycle.get_salescycles_by_last_activity_date(
            crmuser_id, owned=True, mentioned=True, followed=True)
        context['sales_cycles'] = sales_cycles_data[0]
        context['sales_cycle_activities'] = sales_cycles_data[1]
        context['sales_cycle_activity_map'] = sales_cycles_data[2]
        return context


class ShareCreateView(CreateView):

    def form_valid(self, form):
        response = super(self.__class__, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return response

    def get_success_url(self):
        return reverse_lazy('share_list',
                            subdomain=self.request.user_env['subdomain'],
                            kwargs={'slug': 'crm'})


class ShareListView(ListView):

    def get_queryset(self):
        crmuser = self.request.user.get_crmuser()
        return crmuser.in_shares.all()


class ContactDetailView(DetailView):

    def get_object(self):
        contact_pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.get_contact_detail(contact_pk, with_vcard=True)

    def get_context_data(self, **kwargs):
        context = super(ContactDetailView, self).get_context_data(**kwargs)

        current_crmuser = self.request.user.get_crmuser()
        crmusers, users = CRMUser.get_crmusers(with_users=True)

        # show sales_cycle
        sales_cycle_id = self.request.GET.get('sales_cycle_id', False)
        if sales_cycle_id:
            sales_cycle = context['object'].sales_cycles.get(id=sales_cycle_id)
        else:
            sales_cycle = context['object'].sales_cycles.last()
        context['sales_cycle'] = sales_cycle

        # date when first activity was added to the sales_cycle
        d = Activity.get_activities_by_contact(context['object'].pk).first()
        context['first_activity_date'] = d and d.date_created

        # add new activity
        context['activity_form'] = ActivityForm(
            initial={'author': current_crmuser.id,
                     'sales_cycle': sales_cycle.id,
                     'mentioned_user_ids_json': None})

        # add mentions to new activity
        def gen_mentions(crmuser):
            return {'id': crmuser.id,
                    'name': users.get(id=crmuser.user_id).get_username(),
                    'type': 'crmuser'}
        context['mentions'] = json.dumps(map(gen_mentions, crmusers))

        # create new sales_cycle
        context['sales_cycle_form'] = SalesCycleForm(
            initial={'owner': current_crmuser,
                     'contact': context['object']})

        # share contact to
        context['share_form'] = ShareForm(
            initial={'share_from': current_crmuser,
                     'contact': context['object']})
        context['crmusers'] = crmusers.exclude(id=current_crmuser.id)
        context['current_crmuser'] = current_crmuser

        return context


class ContactListView(ListView):

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        crmuser_id = self.request.user.get_crmuser().id
        context['contacts_cold_base'] = self.model.get_cold_base()
        context['contacts_contacted_last_week'] = \
            self.model.get_contacts_for_last_activity_period(
                crmuser_id,
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

    def form_valid(self, form):
        return super(ContactCreateView, self).form_valid(form)


class ContactUpdateView(UpdateView):
    model = Contact
    form_clas = ContactForm
    success_url = reverse_lazy('contact_list')
    template_name = "contact/contact_update.html"


class ContactAddMentionView(UpdateView):
    model = Contact
    form_class = MentionForm  # context_type, context_id
    success_url = reverse_lazy('contact_list')
    template_name = "contact/contact_add_mention.html"

    def post(self, request, *args, **kwargs):
        self.model.objects.get(id=self.kwargs['pk']).add_mention(list(request.POST['user_id']))
        return super(ContactAddMentionView, self).post(request, *args, **kwargs)


class ContactDeleteView(DeleteView):
    model = Contact
    success_url = reverse_lazy('contact_list')
    template_name = 'contact/contact_delete.html'


def contact_export(request, pk, format="html", locale='ru_RU',
                   *args, **kwargs):
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

    def form_valid(self, form):
        response = super(self.__class__, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return response


class SalesCycleUpdateView(UpdateView):
    model = SalesCycle
    form_class = SalesCycleForm
    success_url = reverse_lazy('sales_cycle_list')
    template_name = "sales_cycle/sales_cycle_update.html"


class SalesCycleAddMentionView(UpdateView):
    model = SalesCycle
    form_class = MentionForm  # context_type, context_id
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

    def form_valid(self, form):
        response = super(self.__class__, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return response


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
