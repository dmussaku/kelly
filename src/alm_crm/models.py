import functools
from django.db import models
from django.utils.translation import ugettext_lazy as _
from almanet import settings
from alm_vcard.models import VCard
from django.template.loader import render_to_string
from django.db.models import signals
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
# from dateutil.relativedelta import relativedelta


STATUSES_CAPS = (
    _('new_contact'),
    _('lead_contact'),
    _('opportunity_contact'),
    _('client_contact'))
STATUSES = (NEW, LEAD, OPPORTUNITY, CLIENT) = range(len(STATUSES_CAPS))

ALLOWED_TIME_PERIODS = ['week', 'month', 'year']


class CRMUser(models.Model):

    user_id = models.IntegerField(_('user id'))
    organization_id = models.IntegerField(_('organization id'))
    subscription_id = models.IntegerField(_('subscription id'))
    is_supervisor = models.BooleanField(_('is supervisor'), default=False)

    def get_billing_user(self):
        """Returns a original user.
        Raises:
           User.DoesNotExist exception if no such relation exist"""
        from user.models import User
        user = User.objects.get(pk=self.user_id)
        return user


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
    followers = models.ManyToManyField(
        CRMUser, related_name='following_contacts',
        null=True, blank=True)
    assignees = models.ManyToManyField(
        CRMUser, related_name='assigned_contacts',
        null=True, blank=True)

    # Commented by Rustem K
    # first_name = models.CharField(max_length=31,
    #                               null=False, blank=False)
    # last_name = models.CharField(max_length=30, blank=False)
    # company_name = models.CharField(max_length=50, blank=True)
    # phone = models.CharField(max_length=12, blank=True)
    # email = models.EmailField(unique=True, blank=False)

    # job_address = AddressField(_('job address'), max_length=200, blank=True)
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

    def change_status(self, new_status, save=False):
        """TODO Set status to contact. Return instance (self)"""
        self.status = new_status
        if save:
            self.save()
        return self

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

    def assign_user(self, user_id):
        """Assign user to contact."""
        try:
            user = CRMUser.objects.get(user_id=user_id)
            self.assignees.add(user)
            return True
        except CRMUser.DoesNotExist:
            return False

    @classmethod
    def assign_user_to_contact(cls, user_id, contact_id):
        """TODO Assign user with `user_id` to contact with `contact_id`"""
        return cls.assign_user_to_contacts(user_id, [contact_id])

    @classmethod
    def assign_user_to_contacts(cls, user_id, contact_ids):
        """Assign user `user_id` to set of contacts
        defined by `contact_ids`."""
        assert isinstance(contact_ids, (list, tuple)), 'Must be a list'
        try:
            user = CRMUser.objects.get(user_id=user_id)
            for contact_id in contact_ids:
                try:
                    contact = cls.objects.get(pk=contact_id)
                    contact.assignees.add(user)
                    contact.save()
                except cls.DoesNotExist:
                    pass
            return True
        except CRMUser.DoesNotExist:
            return False

    @classmethod
    def upd_lst_activity_on_create(cls, sender, created=False,
                                   instance=None, **kwargs):
        if not created:
            return
        c = instance.sales_cycle.contact
        c.latest_activity = instance
        c.save()

    @classmethod
    def get_contacts_by_status(cls, status, limit=10, offset=0):
        return Contact.objects.filter(status=status)[offset:offset+limit]

    @classmethod
    def create_contact_with_vcard(cls, contact_attrs, vcard_attrs):
        """TODO Create contact with vcard. Returns True on success."""
        pass

    @classmethod
    def get_contacts_for_last_activity_period(
            cls, user_id, from_dt=None, to_dt=None):
        r"""TODO:
        Retrieves all contacts according to the following criteria:
            - user contacted for that time period (`from_dt`, `to_dt`)
        user contacted means user have activities with at least one
        contact for that period.

        Parameters
        ----------
           user_id - who is contacted
           from_dt - date from
           to_dt - date to

        Returns
        -------
        Queryset of Contacts with whom `user_id` get contacted for that period.
        """
        pass
        # assert periods in ALLOWED_TIME_PERIODS
        # rv = []

        # if 'year' in periods:
        #     rv = queryset_contact.filter(
        #         latest_activity__when__range=(
        #             timezone.now() + relativedelta(months=-12),
        #             timezone.now()))

        # elif 'month' in periods:
        #     rv = queryset_contact.filter(
        #         latest_activity__when__range=(
        #             timezone.now() + relativedelta(months=-1),
        #             timezone.now()))

        # elif 'week' in periods:
        #     grouped['week'] = queryset_contact.filter(
        #         latest_activity__when__range=(
        #             timezone.now() + relativedelta(days=-7),
        #             timezone.now()))

        # return grouped

    @classmethod
    def filter_contacts_by_vcard(cls, search_text, search_params=None,
                                 limit=20, offset=0):
        r"""TODO Make a search query for contacts by their vcard.
        Important! Search params have one of the following formats:
            - name of vcard field, if simple field
            - entity.name of vcard related field, if via foreign key

        Parameters
        ---------
            search_text - text by which we execute a search
            search_params - list of vcard fields [
                'fn', 'organization.unit', 'bday']

            order_by - sort results by fields e.g. ('-pk', '...')
            limit - how much rows must be returned
            offset - from which row to start
        Returns
        -------
            Queryset<Contact> that found by search
            len(Queryset<Contact>) <= limit
        """
        assert isinstance(search_params, list), "Must be a list"
        pass

    @classmethod
    def get_contact_detail(cls, contact_id, with_vcard=False):
        """TODO Returns contact detail by `contact_id`."""
        pass

    @classmethod
    def upload_contacts(cls, upload_type, file_obj, save=False):
        """TODO Extracts contacts from source: vcard file or csv file or any
        other file objects. Build queryset from them and save if required.
        Parameters
        ----------
            upload_type  - csv or vcard or ...
            file_obj - file instance"""
        ALLOWED_CONTACT_UPLOAD_TYPES = ('csv', 'vcard')
        assert upload_type in ALLOWED_CONTACT_UPLOAD_TYPES, ""
        upload_handler = getattr(cls, '_upload_contacts_by_%s' % upload_type)
        contacts = upload_handler(file_obj)
        if save:
            contacts.save()
        return contacts

    @classmethod
    def _upload_contacts_by_vcard(cls, file_obj):
        """Extracts contacts from vcard. Returns Queryset<Contact>."""
        vcard = VCard.importFrom('vCard', file_obj)
        vcard.save()
        contact = cls()
        # contact.save()
        contact.vcard = vcard
        contact.save()
        return contact

    @classmethod
    def _upload_contacts_by_csv(cls, file_obj):
        """TODO Extracts contacts from csv. Returns Queryset<Contact>."""
        pass

    @classmethod
    def get_contacts_by_last_activity_date(
            cls, user_id, include_activities=False, limit=20, offset=0):
        """TODO Returns list of contacts ordered by last activity date.
            Returns:
                Queryset<Contact>
                if includes:
                    Queryset<Activity>
                    contact_activity_map {1: [2], 3: [4, 5, 6]}
            example: (contacts, activities, contact_activity_map)
        """

    @classmethod
    def get_cold_base(cls, limit=20, offset=0):
        """TODO Returns list of contacts that are considered cold.
        Cold contacts should satisfy two conditions:
            1. no assignee for contact
            2. status is NEW"""
        return cls.objects.filter(
            assignees__isnull=True, status=NEW)[offset:offset+limit]


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


class Product(models.Model):
    title = models.CharField(_('product title'), max_length=100, blank=False)
    description = models.TextField(_('product description'))

    class Meta:
        verbose_name = _('product')
        db_table = settings.DB_PREFIX.format('product')

    def __unicode__(self):
        return self.title


class SalesCycle(models.Model):
    STATUS_OPTIONS = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('N', 'New'),
        )
    products = models.ManyToManyField(Product,
                                      related_name='sales_cycles')
    owner = models.ForeignKey(CRMUser, related_name='owned_sales_cycles')
    followers = models.ManyToManyField(
        CRMUser, related_name='follow_sales_cycles',
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

    def assign_user(self, user_id, save=False):
        """TODO Assign user to salescycle."""
        pass

    def get_activities(self, limit=20, offset=0):
        """TODO Returns list of activities ordered by date."""
        return self.rel_activities.order_by('-when')[offset:offset + limit]

    def add_product(self, product_id, **kw):
        """TODO Assigns products to salescycle"""
        try:
            product = Product.objects.get(id=product_id)
            self.products.add(product)
            return True
        except Product.DoesNotExist:
            return False

    def add_products(self, product_ids=None, save=False):
        """TODO Assigns products to salescycle"""
        assert isinstance(product_ids, (tuple, list)), "must be a list"
        return [self.add_products(pid) for pid in product_ids]

    def set_result(self, value_obj, save=False):
        """TODO Set salescycle.real_value to value_obj. Saves the salescycle
        if `save` is true"""
        pass

    def add_follower(self, user_id, **kw):
        """TODO Set follower to salescycle"""
        return self.add_followers([user_id], **kw)

    def add_followers(self, user_ids, save=False):
        """TODO Set followers to salescycle"""
        assert isinstance(user_ids, (tuple, list)), 'must be a list'

    @classmethod
    def upd_lst_activity_on_create(cls, sender,
                                   created=False, instance=None, **kwargs):
        if not created:
            return
        sales_cycle = instance.sales_cycle
        sales_cycle.latest_activity = sales_cycle.find_latest_activity()
        sales_cycle.save()

    @classmethod
    def get_salescyles_by_last_activity_date(
            cls, user_id, limit=20, offset=0):
        """TODO Returns user salescycles ordered by last activity date.

            Returns
            -------
                Queryset<SalesCycle>
                Queryset<Activity>
                sales_cycle_activity_map =  {1: [2, 3, 4], 2:[3, 5, 7]}
        """
        pass

    @classmethod
    def get_salescycles_by_contact(cls, contact_id, limit=20, offset=0):
        """TODO Returns queryset of sales cycles by contact"""
        pass


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
    author = models.ForeignKey(CRMUser, related_name='owned_activities')

    class Meta:
        verbose_name = 'activity'
        db_table = settings.DB_PREFIX.format('activity')

    def __unicode__(self):
        return self.title

    def set_feedback(self, feedback_obj, save=False):
        """Set feedback to activity instance. Saves if `save` is set(True)."""
        pass

    @classmethod
    def get_activities_by_contact(cls, contact_id):
        return Activity.objects.filter(sales_cycle__contact_id=contact_id)

    @classmethod
    def get_activities_by_salescycle(cls, sales_cycle_id, limit=20, offset=0):
        """TODO Returns list of activities by sales cycle id."""
        pass

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

    @classmethod
    def get_activity_detail(
            cls, activity_id, include_sales_cycle=False,
            include_mentioned_users=False, include_comments=True):
        """TODO Returns activity details with comments by default.
        If `include_mentioned_users` is ON, then includes mentioned user.
        If `include_sales_cycle` is ON, then include its sales cycle.

        Returns
        --------
            activity - Activity object
            sales_cycle (if included)
            comments (if included)
            mentioned_users (if included)
            {'activity': {'object': ..., 'comments': [], sales_cycle: ..}}
        """

    @classmethod
    def get_number_of_activities_by_day(cls, user_id,
                                        from_dt=None, to_dt=None):
        """TODO
        Returns
        -------
            {'2018-22-05': 12, '2018-22-06': 14, ...}
        """


class Mention(models.Model):
    user_id = models.IntegerField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s %s" % (self.user_id, self.content_object)

    @classmethod
    def build_new(cls, user_id, content_class=None,
                  object_id=None, save=False):
        mention = cls(user_id=user_id)
        mention.content_type = ContentType.objects.get_for_model(content_class)
        mention.object_id = object_id
        if save:
            mention.save()
        return mention

    @classmethod
    def get_all_mentions_of(cls, user_id):
        """TODO Returns all mentions of user.
        Returns
        ----------
            Queryset<Mention>
        """
        pass


class Comment(models.Model):
    comment = models.CharField(max_length=140)
    author = models.ForeignKey(CRMUser, related_name='comment_author')
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

    @classmethod
    def get_comments_by_context(cls, context_object_id, context_class,
                                limit=20, offset=0):
        """TODO Returns list of comments by context."""
        pass


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
