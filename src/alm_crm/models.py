import functools
from django.db import models
from django.utils.translation import ugettext_lazy as _
from almanet import settings
from alm_user.models import User
from almanet.models import Product
from django.template.loader import render_to_string

# import vcard as django_vcard

from django.db.models import signals
from django.dispatch import receiver
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from dateutil.relativedelta import relativedelta


STATUSES_CAPS = (
    _('new_contact'),
    _('lead_contact'),
    _('opportunity_contact'),
    _('client_contact'))
STATUSES = (NEW, LEAD, OPPORTUNITY, CLIENT) = range(len(STATUSES_CAPS))


class Contact(models.Model):

    STATUS_CODES = zip(STATUSES, STATUSES_CAPS)
    TYPES = (COMPANY_TP, USER_TP) = ('co', 'user')
    TYPES_WITH_CAPS = ((COMPANY_TP, _('company type')),
                       (USER_TP, _('user type')))
    status = models.IntegerField(
        _('contact status'),
        max_length=30,
        choices=STATUS_CODES, default=NEW)
    tp = models.CharField(
        _('contact type'),
        max_length=30,
        choices=TYPES_WITH_CAPS, default=USER_TP)
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    vcard = models.ForeignKey('alm_vcard.VCard', blank=True, null=True)
    company_contact = models.ForeignKey(
        'Contact', blank=True, null=True, related_name='user_contacts')

    # Commented by Rustem K
    # first_name = models.CharField(max_length=31,
    #                               null=False, blank=False)
    # last_name = models.CharField(max_length=30, blank=False)
    # company_name = models.CharField(max_length=50, blank=True)
    # phone = models.CharField(max_length=12, blank=True)
    # email = models.EmailField(unique=True, blank=False)

    # job_address = AddressField(_('job address'), max_length=200, blank=True)
    status = models.IntegerField(
        _('contact status'), max_length=30, choices=enumerate(STATUSES), default=NEW)
    latest_activity = models.OneToOneField(
        'Activity', on_delete=models.SET_NULL,
        related_name='contact_latest_activity', null=True)
    mentions = generic.GenericRelation('Mention')

    class Meta:
        verbose_name = _('contact')
        db_table = settings.DB_PREFIX.format('contact')

    def __unicode__(self):
        return "%s %s" % (self.vcard, self.tp)

    @property
    def name(self):
        if not self.vcard:
            return 'Unknown'
        return self.vcard.fn

    def get_tp(self):
        return dict(self.TYPES_WITH_CAPS).get(self.tp, None)

    def is_new(self):
        return self.status == NEW

    def is_lead(self):
        return self.status == LEAD

    def is_opportunity(self):
        return self.status == OPPORTUNITY

    def is_client(self):
        return self.status == CLIENT

    def export_to(self, tp, **options):
        if not tp in ('html', 'vcard'):
            return False
        exporter = getattr(self, 'to_{}'.format(tp))
        return exporter(**options)

    def to_vcard(self, locale='ru_RU'):
        return self.vcard.exportTo('vCard')

    def to_html(self, locale='ru_RU'):
        tpl_name = 'vcard/_detail.%s.html' % locale
        context = {'object': self.vcard}
        return render_to_string(tpl_name, context)

    def get_latest_activity(self):
        return self.sales_cycles.aggregate(Max('contact_latest_activity'))

    @receiver(signals.post_save, sender='Activity')
    def set_latest_activity(sender, instance, created, **kwargs):
        if created:
            contact = instance.sales_cycle.contact
            contact.latest_activity = instance
            contact.save()

    def find_latest_activity(self):
        """Find latest activity among all sales_cycle_contacts."""
        sales_cycle = self.sales_cycles.order_by(
            'latest_activity__when').first()
        return sales_cycle and sales_cycle.latest_activity or None

    def add_mention(self, user_ids=None):
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        build_single_mention = functools.partial(Mention.build_new,
                                                 content_class=self.__class__,
                                                 object_id=self.pk,
                                                 save=True)
        self.mentions = map(build_single_mention, user_ids)
        self.save()

    @classmethod
    def upd_lst_activity_on_create(cls, sender, created=False,
                                   instance=None, **kwargs):
        if not created:
            return
        c = instance.sales_cycle.contact
        c.latest_activity = instance
        c.save()

    @classmethod
    def group_contacts_by_status(cls, status, limit=10, offset=0):
        return Contact.objects.filter(status=status)[offset:limit]

    @classmethod
    def group_contacts_by_activity_period(cls, queryset_contact,
                                          periods=['week', 'month', 'year']):
        grouped = {}

        if 'year' in periods:
            grouped['year'] = queryset_contact.filter(
                latest_activity__when__range=(
                    timezone.now() + relativedelta(months=-12),
                    timezone.now()))

        if 'month' in periods:
            grouped['month'] = queryset_contact.filter(
                latest_activity__when__range=(
                    timezone.now() + relativedelta(months=-1),
                    timezone.now()))

        if 'week' in periods:
            grouped['week'] = queryset_contact.filter(
                latest_activity__when__range=(
                    timezone.now() + relativedelta(days=-7),
                    timezone.now()))

        return grouped


class Value(models.Model):
    # Type of payment
    SALARY_OPTIONS = (
        ('monthly', 'Monthly'),
        ('annualy', 'Annualy'),
        ('instant', 'Instant'),
    )
    CURRENCY_OPTIONS = (
        ('USD', 'US Dollar'),
        ('RUB', 'Rubbles'),
        ('KZT', 'Tenge'),
        )
    salary = models.CharField(max_length=7, choices=SALARY_OPTIONS,
                              default='instant')
    amount = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS,
                                default='KZT')

    class Meta:
        verbose_name = 'value'
        db_table = settings.DB_PREFIX.format('value')

    def __unicode__(self):
        return "%s %s %s" % (self.amount, self.currency, self.salary)


class SalesCycle(models.Model):
    STATUS_OPTIONS = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('N', 'New'),
        )
    products = models.ManyToManyField(Product,
                                      related_name='sales_cycles')
    owner = models.ForeignKey(User, related_name='owned_sales_cycles')
    followers = models.ManyToManyField(
        User, related_name='follow_sales_cycles',
        null=True, blank=True)
    contact = models.ForeignKey(
        Contact, related_name='sales_cycles',
        on_delete=models.SET_DEFAULT, default=None)
    latest_activity = models.OneToOneField('Activity',
                                           blank=True, null=True,
                                           on_delete=models.SET_NULL)
    projected_value = models.OneToOneField(
        Value, related_name='_unused_1_sales_cycle', null=True)
    real_value = models.OneToOneField(
        Value, related_name='_unused_2_sales_cycle',
        null=True, blank=True,)
    status = models.CharField(max_length=2,
                              choices=STATUS_OPTIONS, default='N')
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    from_date = models.DateTimeField(blank=False, auto_now_add=True)
    to_date = models.DateTimeField(blank=False, auto_now_add=True)
    mentions = generic.GenericRelation('Mention')

    class Meta:
        verbose_name = 'sales_cycle'
        db_table = settings.DB_PREFIX.format('sales_cycle')

    def find_latest_activity(self):
        return self.rel_activities.order_by('-when').first()

    def __unicode__(self):
        return '%s %s' % (self.contact, self.status)

    # Adds mentions to a current class, takes a lsit of user_ids as an input
    # and then runs through the list and calls the function build_new which
    # is declared in Mention class
    def add_mention(self, user_ids=None):
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        build_single_mention = functools.partial(Mention.build_new,
                                                 content_class=self.__class__,
                                                 object_id=self.pk,
                                                 save=True)
        self.mentions = map(build_single_mention, user_ids)
        self.save()

    @classmethod
    def upd_lst_activity_on_create(cls, sender,
                                   created=False, instance=None, **kwargs):
        if not created:
            return
        sales_cycle = instance.sales_cycle
        sales_cycle.latest_activity = sales_cycle.find_latest_activity()
        sales_cycle.save()


class Activity(models.Model):
    STATUS_OPTIONS = (
        ('W', 'waiting'),
        ('$', '1000'),
        ('1', 'Client is happy'),
        ('2', 'Client is OK'),
        ('3', 'Client is neutral'),
        ('4', 'Client is disappointed'),
        ('5', 'Client is angry')
    )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    when = models.DateTimeField(blank=True, auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_OPTIONS, default='')
    feedback = models.CharField(max_length=300)
    sales_cycle = models.ForeignKey(SalesCycle,
                                    related_name='rel_activities')
    author = models.ForeignKey(User, related_name='owned_activities')

    @classmethod
    def get_activities_by_contact(cls, contact_id):
        return Activity.objects.filter(sales_cycle__contact_id=contact_id)

    @classmethod
    def get_mentioned_activities_of(cls, user_ids=set([])):
        """
        to get filter with OR statements, like below:
            Activity.objects.filter(
                Q(sales_cycle__mentions__id=user_ids[0]) |
                Q(sales_cycle__mentions__id=user_ids[1])
            )
        used functional python's reduce
        """

        q = reduce(lambda q, f: q | models.Q(sales_cycle__mentions__id=f),
                   user_ids, models.Q())

        return Activity.objects.filter(q)

    class Meta:
        verbose_name = 'activity'
        db_table = settings.DB_PREFIX.format('activity')

    def __unicode__(self):
        return self.title


class Mention(models.Model):
    user_id = models.IntegerField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s %s" % (self.user_id, self.content_object)

    @classmethod
    def build_new(cls, user_id, content_class=None, object_id=None, save=False):
        mention = cls(user_id=user_id)
        mention.content_type = ContentType.objects.get_for_model(content_class)
        mention.object_id = object_id
        if save:
            mention.save()
        return mention


class Comment(models.Model):
    comment = models.CharField(max_length=140)
    author = models.ForeignKey(User, related_name='comment_author')
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    date_edited = models.DateTimeField(blank=True)
    object_id = models.IntegerField(null=True, blank=False)
    content_type = models.CharField(max_length=1000, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    mentions = generic.GenericRelation('Mention')

    def __unicode__(self):
        return "%s's comment" % (self.author)

    def save(self, **kwargs):
        if self.date_created:
            self.date_edited = timezone.now()
        super(Comment, self).save(**kwargs)

    def add_mention(self, user_ids=None):
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        build_single_mention = functools.partial(Mention.build_new,
                                                 content_class=self.__class__,
                                                 object_id=self.pk,
                                                 save=True)
        self.mentions = map(build_single_mention, user_ids)
        self.save()

    @classmethod
    def build_new(cls, user_id, content_class=None,
                  object_id=None, save=False):
        comment = cls(user_id=user_id)
        comment.content_type = ContentType.objects.get_for_model(content_class)
        comment.object_id = object_id
        if save:
            comment.save()
        return comment


class CRMUser(models.Model):

    user_id = models.IntegerField(_('user id'))
    is_supervisor = models.BooleanField(_('is supervisor'), default=False)

    def get_billing_user(self):
        """Returns a original user.
        Raises:
           User.DoesNotExist exception if no such relation exist"""
        from user.models import User
        user = User.objects.get(pk=self.user_id)
        return user


signals.post_save.connect(
    Contact.upd_lst_activity_on_create, sender=Activity)
signals.post_save.connect(
    SalesCycle.upd_lst_activity_on_create, sender=Activity)


def on_activity_delete(sender, instance=None, **kwargs):
    sales_cycle = instance.sales_cycle
    sales_cycle.latest_activity = sales_cycle.find_latest_activity()
    sales_cycle.save()

    contact = sales_cycle.contact
    contact.latest_activity = contact.find_latest_activity()
    contact.save()

signals.post_delete.connect(on_activity_delete, sender=Activity)
