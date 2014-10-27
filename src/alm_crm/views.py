import json
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from almanet.url_resolvers import reverse_lazy, reverse as almanet_reverse
from almanet import settings
from models import (
    Contact,
    SalesCycle,
    Activity,
    Feedback,
    Comment,
    Value,
    CRMUser,
    Product,
    Share
    )
from forms import (
    ContactForm,
    SalesCycleForm,
    MentionForm,
    ActivityForm,
    CommentForm,
    ActivityFeedbackForm,
    ShareForm,
    ValueForm,
    )
from alm_vcard.forms import VCardUploadForm
from django.shortcuts import render_to_response
from alm_vcard.models import VCard
from alm_vcard.forms import VCardForm


class DashboardView(View):

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['subdomain'] = self.request.user_env['subdomain']
        return context

    def get(self, request, *a, **kw):
        return HttpResponseRedirect(almanet_reverse(
            'feed',
            kwargs={'service_slug': settings.DEFAULT_SERVICE},
            subdomain=request.user_env['subdomain'])
        )


class FeedView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(FeedView, self).get_context_data(**kwargs)

        crmuser_id = self.request.user.get_crmuser().id
        sales_cycles_data = SalesCycle.get_salescycles_by_last_activity_date(
            crmuser_id, owned=False, mentioned=True, followed=True)
        context['feed_activities'] = sales_cycles_data[1]

        return context


class FeedMentionsView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        crmuser = self.request.user.get_crmuser()
        context['mentioned_activities'] = \
            Activity.get_mentioned_activities_of(crmuser.id)
        return context


class FeedCompanyView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        env = self.request.user_env

        def find_pk(pk):
            if (env['subscription_{}'.format(pk)]['slug'] == kwargs['service_slug']):
                return pk
        subscription_id = map(find_pk, env['subscriptions'])[0]

        context['company_activities'] = \
            Activity.get_activities_by_subscription(subscription_id)
        return context


class ProfileView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        crmuser = self.request.user.get_crmuser()
        crmuser_user = crmuser.get_billing_user()
        context['profile_info'] = {
            'fn': crmuser_user.get_full_name(),
            'company': crmuser_user.get_company(),
            'email_work': crmuser_user.email,
            'mobile': ''
        }

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
                            kwargs={'service_slug': settings.DEFAULT_SERVICE})


class ShareListView(ListView):

    def get_queryset(self):
        crmuser = self.request.user.get_crmuser()
        return Share.get_shares_in_for(crmuser.pk)


class ContactDetailView(DetailView):

    def get_object(self):
        contact_pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.get_contact_detail(contact_pk, with_vcard=True)

    def get_context_data(self, **kwargs):
        context = super(ContactDetailView, self).get_context_data(**kwargs)

        current_crmuser = self.request.user.get_crmuser()

        # get first sales_cycle on open
        sales_cycle_id = self.request.GET.get('sales_cycle_id', None)
        if not sales_cycle_id is None:
            context['sales_cycle'] = SalesCycle.objects.get(pk=sales_cycle_id)
        else:
            # last sales_cycle
            context['sales_cycle'] = \
                SalesCycle.get_salescycles_of_contact_by_last_activity_date(
                    context['object'].id).first()

        # create new sales_cycle to contact
        context['new_sales_cycle_form'] = SalesCycleForm(
            initial={'owner': current_crmuser,
                     'contact': context['object']})

        # share contact
        context['share_form'] = ShareForm(
            initial={'share_from': current_crmuser,
                     'contact': context['object']})
        crmusers = CRMUser.get_crmusers()
        context['crmusers'] = crmusers.exclude(id=current_crmuser.id)
        context['current_crmuser'] = current_crmuser

        return context


class ContactListView(ListView):

    def get_queryset(self):
        contacts = self.model.objects.all()
        return contacts


class ContactSearchListView(ListView):

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        try:
            context['contacts'] = Contact().filter_contacts_by_vcard(
                self.request.GET['query'],
                [('given_name','startswith'),
                ('family_name','startswith'),
                ('email__value','icontains'),
                ('tel__value','icontains'),
                ('org__organization_name','startswith')
                ]
                ).order_by('vcard__given_name')
        except:
            context['contacts'] = Contact.objects.all().order_by('vcard__given_name')
        return context


def contact_create_view(request, service_slug):
    if request.method == 'GET':
        return render_to_response('crm/contacts/contact_create.html',{'vcard_form':VCardForm, 'csrf_token':request.META['CSRF_COOKIE']})
    if request.method == 'POST':
        vcard_form = VCardForm(request.POST, instance=VCard())
        if vcard_form.is_valid():
            v = vcard_form.save()
            c = Contact(owner=request.user.get_crmuser(), vcard=v)
            c.save()
            return HttpResponse(json.dumps({'vcard_id':v.id, 'contact_id':c.id}), mimetype='application/json')
        return HttpResponse('no success')
        # if vcard_form.is_valid():
        #     v = vcard_form.save()
        #     c = Contact(owner=request.user.get_crmuser(), vcard=v)
        #     c.save()
        #     return HttpResponseRedirect(
        #         almanet_reverse(
        #             'contact_detail',
        #             kwargs={'service_slug': settings.DEFAULT_SERVICE, 'contact_pk':c.pk},
        #             subdomain=request.user_env['subdomain']
        #             )
        #         )

class ContactUpdateView(UpdateView):
    model = VCard
    form_class = VCardForm
    template_name = 'crm/contacts/contact_update.html'
    pk_url_kwarg = 'contact_pk'

    def get_queryset(self):
        return VCard.objects.all()

    def get_object(self, **kwargs):
        return Contact.objects.get(id=self.kwargs['contact_pk']).vcard

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        v = Contact.objects.get(id=self.kwargs['contact_pk']).vcard
        context['emails'] = v.email_set.all()
        context['tels'] = v.tel_set.all()
        context['orgs'] = v.org_set.all()
        print context
        return context

    def get_success_url(self):
        return reverse_lazy('contact_list',
                            subdomain=self.request.user_env['subdomain'],
                            kwargs={'service_slug': settings.DEFAULT_SERVICE})


def comment_create_view(request, service_slug, content_type, object_id):
    from django.template import RequestContext

    if request.method == 'GET':
        crmusers, users = CRMUser.get_crmusers(with_users=True)
        gen_mentions = lambda crmuser: {
            'id': crmuser.id,
            'name': users.get(id=crmuser.user_id).get_username(),
            'type': 'crmuser'
        }
        mentions_json = json.dumps(map(gen_mentions, crmusers))

        if (content_type == 'activity'):
            return render_to_response('crm/comments/comment_list.html',
                    {'comments': Comment().get_comments_by_context(object_id, content_type),
                     'activity_id': object_id,
                     'mentions_json': mentions_json},
                    context_instance=RequestContext(request)
                )
        elif (content_type == 'share'):
            return render_to_response('crm/share/comment/comment_list.html',
                    {'comments':Comment().get_comments_by_context(object_id, content_type),
                     'share_id':object_id},
                    context_instance=RequestContext(request)
                )
        elif (content_type == 'contact'):
            return render_to_response('crm/share/comment/comment_list.html',
                    {'comments':Comment().get_comments_by_context(object_id, content_type),
                     'share_id':object_id},
                    context_instance=RequestContext(request)
                )
    if request.method == 'POST':
        comment = Comment(
            comment=request.POST['comment'],
            author=request.user.get_crmuser(),
            content_type_id=ContentType.objects.get(model=content_type).id,
            object_id=object_id
            )
        try:
            comment.save()

            try:
                mentions_ids = json.loads(request.POST['mention_ids'])
            except:
                mentions_ids = []
            comment.add_mention(mentions_ids)

            return HttpResponse('Success')
        except:
            return HttpResponse('No Success')


def comment_delete_view(request, service_slug):
    if request.method == 'POST':
        try:
            comment = Comment.objects.get(id=request.POST['id'])
            comment.delete()
            return HttpResponse('success')
        except:
            return HttpResponse('no success')


def comment_edit_view(request, service_slug):
    if request.method == 'GET':
        return HttpResponse('GET')
    if request.method == 'POST':
        try:
            comment = Comment.objects.get(id=request.POST['id'])
            comment.comment = request.POST['comment']
            comment.save()
            return HttpResponse('success')
        except:
            return HttpResponse('no success')


class CommentCreateView(CreateView):
    '''
    def get_initial(self):
       return {'author' : self.request.user}
    '''

    def form_valid(self, form):
        form.instance.author = self.request.user.get_crmuser()
        form.instance.content_type_id = ContentType.objects.get(model=self.kwargs['content_type']).id
        form.instance.object_id = self.kwargs['object_id']
        try:
            comment = form.save()
            data = json.dumps({
                'author': comment.author.id,
                'name': comment.author.get_billing_user().get_full_name(),
                'date_created': comment.date_created.strftime('%Y-%m-%dT%H:%M:%S'),
                'object_id': comment.object_id,
                'id': comment.id,
                'comment': comment.comment
                })
            return HttpResponse(data, content_type="application/json")
        except:
            return super(CommentCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return almanet_reverse(
            'feed',
            kwargs={'service_slug': settings.DEFAULT_SERVICE},
            subdomain=self.request.user_env['subdomain']
            )

    def get_context_data(self, **kwargs):
        context = super(CommentCreateView, self).get_context_data(**kwargs)
        context['context_type'] = self.kwargs['content_type']
        context['object_id'] = self.kwargs['object_id']
        context['comments'] = Comment().get_comments_by_context(self.kwargs['object_id'], self.kwargs['content_type'])
        return context






def contact_search(request, slug, query_string):
    if request.method == 'GET':

        queryset = Contact.objects.filter(Q(vcard__given_name__startswith=query_string) |
            Q(vcard__family_name__startswith=query_string) |
            Q(vcard__tel__value__contains=query_string) |
            Q(vcard__email__value__startswith=query_string) |
            Q(vcard__org__organization_name__startswith=query_string)
            )
        json_list=[contact.json_serialize() for contact in queryset]
        return HttpResponse(json.dumps(json_list), content_type='application/json')


class CommentAddMentionView(CreateView):
    model = Comment
    form_class = MentionForm  # context_type, context_id
    success_url = reverse_lazy('comment_list')
    template_name = "comment/comment_add_mention.html"

    def post(self, request, *args, **kwargs):
        self.model.objects.get(id=self.kwargs['pk']).add_mention(list(request.POST['user_id']))
        return super(CommentAddMentionView, self).post(request, *args, **kwargs)


class UserProductView(ListView):

    def get_queryset(self):
        u = self.request.user
        subscrs = u.get_active_subscriptions().filter(
            service__slug=self.kwargs['service_slug'])
        return subscrs


class ContactCreateView(CreateView):

    def form_valid(self, form):
        return super(ContactCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('contacts_list',
                            subdomain=self.request.user_env['subdomain'],
                            kwargs={'service_slug': settings.DEFAULT_SERVICE})



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

    success_url = reverse_lazy('sales_cycle_list')

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

    def get_object(self):
        sales_cycle_pk = self.request.GET.get('sales_cycle_id', None)
        return self.model.objects.get(pk=sales_cycle_pk)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        current_crmuser = self.request.user.get_crmuser()
        sales_cycle = context['object']
        contact = sales_cycle.contact

        # list of contact sales_cycles
        context['sales_cycles'] = \
            SalesCycle.get_salescycles_of_contact_by_last_activity_date(
                contact.id)

        # create new sales_cycle to contact
        context['new_sales_cycle_form'] = SalesCycleForm(
            initial={'owner': current_crmuser,
                     'contact': contact})

        # date when first activity was added to the sales_cycle
        context['first_activity_date'] = sales_cycle.get_first_activity_date()

        # activities of the sales_cycle
        context['activities'] = sales_cycle.get_activities(limit=100)

        # add new activity to current salescycle
        context['activity_form'] = ActivityForm(
            initial={'author': current_crmuser,
                     'sales_cycle': sales_cycle.pk,
                     'mentioned_user_ids_json': None})

        # add mentions to new activity
        crmusers, users = CRMUser.get_crmusers(with_users=True)

        def gen_mentions(crmuser):
            return {'id': crmuser.id,
                    'name': users.get(id=crmuser.user_id).get_username(),
                    'type': 'crmuser'}
        context['activity_mentions_json'] = \
            json.dumps(map(gen_mentions, crmusers))

        # add new value to current salescycle
        if sales_cycle.real_value is None:
            context['value_form'] = ValueForm(
                initial={'owner': current_crmuser, 'amount': 0})
        else:
            context['value_form'] = ValueForm(instance=sales_cycle.real_value)

        # add products to current salescycle
        context['product_datums'] = json.dumps(list(Product.get_products()
                                               .values('pk', 'name')))
        context['sales_cycle_products'] = sales_cycle.products.all()

        # mentions, add mentions(followers) to sales_cycle:
        if sales_cycle is None:
            context['mentioned'] = None
        else:
            context['mentioned'] = sales_cycle.get_mentioned_users()

        # crmusers to mention sales_cycle
        context['crmusers'] = crmusers

        return context


class SalesCycleDeleteView(DeleteView):
    model = SalesCycle
    success_url = reverse_lazy('sales_cycle_list')
    template_name = 'sales_cycle/sales_cycle_delete.html'


def sales_cycle_value_update(request, service_slug=None, sales_cycle_pk=None):
    sales_cycle = get_object_or_404(SalesCycle, pk=sales_cycle_pk)

    if request.method == 'POST':
        value_form = ValueForm(request.POST, instance=sales_cycle.real_value)
        if value_form.is_valid():
            value_form.save()
            if sales_cycle.real_value is None:
                sales_cycle.real_value = value_form.instance
                sales_cycle.save()

            data = {
                'pk': value_form.instance.pk,
                'sales_cycle_pk': sales_cycle.pk
            }
            return HttpResponse(json.dumps(data), mimetype="application/json")


def sales_cycle_add_mention(request, service_slug=None, sales_cycle_pk=None):
    sales_cycle = get_object_or_404(SalesCycle, pk=sales_cycle_pk)

    if request.method == 'POST':
        crmuser_id = request.POST.get('id', None)
        if not crmuser_id is None:
            sales_cycle.add_mention(crmuser_id)
        data = {
            'pk': crmuser_id,
            'sales_cycle_pk': sales_cycle.pk
        }
        return HttpResponse(json.dumps(data), mimetype="application/json")


def sales_cycle_add_product(request, service_slug=None, sales_cycle_pk=None):
    sales_cycle = get_object_or_404(SalesCycle, pk=sales_cycle_pk)

    if request.method == 'POST':
        product_id = request.POST.get('product_id', None)
        if not product_id is None:
            sales_cycle.add_product(product_id)
        data = {
            'pk': product_id,
            'sales_cycle_pk': sales_cycle.pk
        }
        return HttpResponse(json.dumps(data), mimetype="application/json")


def sales_cycle_remove_product(request, service_slug=None,
                               sales_cycle_pk=None):
    sales_cycle = get_object_or_404(SalesCycle, pk=sales_cycle_pk)

    if request.method == 'POST':
        product_id = request.POST.get('product_id', None)
        status = False
        if not product_id is None:
            status = sales_cycle.remove_products(product_id)

        data = {
            'status': status,
            'pk': product_id,
            'sales_cycle_pk': sales_cycle.pk
        }
        return HttpResponse(json.dumps(data), mimetype="application/json")


class ActivityCreateView(CreateView):

    success_url = reverse_lazy('activity_list')

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

    def get_context_data(self, **kwargs):
        context = super(ActivityDetailView, self).get_context_data(**kwargs)
        context['activity'] = Activity.objects.get(id=self.kwargs['pk'])
        context['comments'] = Activity.objects.get(id=self.kwargs['pk']).comments.all()
        context['comment_form'] = CommentForm
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


def comments_by_activity(self, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
    except ObjectDoesNotExist:
        return False
    else:
        comments = Comment().get_comments_by_context(activity.id, Activity)
    if request.method == 'POST':
        pass

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
