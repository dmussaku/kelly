from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, UserManager as contrib_user_manager)
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from timezone_field import TimeZoneField
from almanet.models import Subscription
from alm_vcard.models import VCard, Email
from datetime import datetime



class AccountManager(contrib_user_manager):
    def create_user(self, email, password, user, company, is_admin=False):
        acc = Account(email=email, is_admin=is_admin, user=user, company=company)
        acc.set_password(password)
        acc.save()
        return acc


class Account(AbstractBaseUser):

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'email'

    email = models.EmailField(blank=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)

    company = models.ForeignKey('alm_company.Company', related_name='accounts')
    user = models.ForeignKey('User', related_name='accounts')

    class Meta:
        verbose_name = 'account'
        db_table = settings.DB_PREFIX.format('account')

    objects = AccountManager()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def get_short_name(self):
        return self.user.get_short_name()

    def get_full_name(self):
        return self.user.get_full_name()

    def get_username(self):
        return self.email


    def is_authenticated(self):
        return True

    def has_module_perms(self, module):
        if self.is_admin:
            return True
        return False

    def has_perm(self, perm, obj=None):
        return self.is_admin



class UserManager(contrib_user_manager):
    def create_user(self, first_name, last_name):
        user = User(first_name=first_name, last_name=last_name)
        user.save()
        return user


class User(AbstractBaseUser):

    #REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'id'
    first_name = models.CharField(_('first name'), max_length=31,
                                  null=False, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    # email = models.EmailField(_('email address'), unique=True, blank=False)
    # is_active = models.BooleanField(_('active'), default=True)

    timezone = TimeZoneField(default='Asia/Almaty')

    # company = models.ManyToManyField('alm_company.Company',
    #                                  related_name='users')
    # is_admin = models.BooleanField(default=False)

    vcard = models.OneToOneField(VCard, blank=True, null=True)
    userpic = models.ImageField(upload_to='userpics')

    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True, blank=True)

    is_supervisor = models.BooleanField(_('is supervisor'), default=False)
    unfollow_list = models.ManyToManyField(
        'alm_crm.Contact', #related_name='followers',
        null=True, blank=True
        )

    class Meta:
        verbose_name = _('user')
        db_table = settings.DB_PREFIX.format('user')

    objects = UserManager()

    def save(self, *a, **kw):
        is_created = not hasattr(self, 'pk') or not self.pk
        super(User, self).save(*a, **kw)
        if is_created:
            vc = VCard(
                fn=self.first_name + " " + self.last_name,
                family_name=self.last_name,
                given_name=self.first_name)
            vc.save()
            ## TODO: how get self.email
            # email = Email(vcard=vc, type=Email.PREF, value=self.email)
            # email.save()
            self.vcard = vc
            self.save()

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_username(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_subscriptions(self, flat=False):
        subscriptions = self.subscriptions.all()
        if not flat:
            return subscriptions
        else:
            data = {}
            for s in subscriptions:
                data[s.service.slug] = {'id': s.id, 'is_active': s.is_active}
            return data

    def get_active_subscriptions(self, flat=False):
        return self.subscriptions.filter(is_active=True)

    def connected_services(self):
        return [subscr.service for subscr in self.get_active_subscriptions()]

    def is_service_connected(self, service):
        return service in self.connected_services()

'''
    def connect_service(self, service):
        co = self.company.first()
        try:
            s = Subscription.objects.get(
                service=service, organization=co)
        except Subscription.DoesNotExist:
            s = Subscription(service=service, user=self, organization=co)
        finally:
            s.is_active = True
            s.save()
            service_user = self.get_subscr_user(s.pk)
            if service_user is None:
                # create user in corresponding service
                # eg.: CRMUser in CRM service, CRM's slug = crm
                create_user = getattr(self,
                                      'create_{}user'.format(service.slug))
                service_user = create_user(s.pk, self.get_company().pk)

    def disconnect_service(self, service):
        s = self.subscriptions.filter(is_active=True, service=service).first()
        if s:
            s.is_active = False
            s.save()

    def get_subscr_by_service(self, service):
        return Subscription.objects.get(service=service, organization=self.company.first())
'''
    # def create_crmuser(self, subscription_pk, organization_pk):
    #     from alm_crm.models import CRMUser
    #     # this should be further resolved when multiple database will be configured
    #     # and DecoupledModel applied to connect User and CRMUser
    #     # if not self.crmuser and self.is_active:
    #     crmuser = CRMUser(user_id=self.pk,
    #                       is_supervisor=True,
    #                       subscription_id=subscription_pk,
    #                       organization_id=organization_pk)
    #     crmuser.save()
    #     # self.crmuser = crmuser
    #     self.save()
    #     return crmuser  # self.crmuser

    # def get_subscr_user(self, subscription_id):
    #     from alm_crm.models import CRMUser
    #     try:
    #         return CRMUser.objects.get(user_id=self.pk,
    #                                    subscription_id=subscription_id)
    #     except CRMUser.DoesNotExist:
    #         return None

    # def get_crmuser(self):
    #     from alm_crm.models import CRMUser
    #     return CRMUser.objects.get(user_id=self.pk)


class Referral(models.Model):
    email = models.EmailField()
    date_created = models.DateTimeField(blank=True, auto_now_add=True)
    referer = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        verbose_name = _('referral')
        db_table = settings.DB_PREFIX.format('referral')

    def __unicode__(self):
        return u'%s'%self.email

