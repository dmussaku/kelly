#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
from tastypie import fields, http
from tastypie.bundle import Bundle
from tastypie.resources import Resource, ModelResource
from tastypie.exceptions import NotFound, BadRequest
from tastypie.utils import trailing_slash
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.http import HttpNotFound
from tastypie.serializers import Serializer

from django.contrib.auth import login, authenticate
from django.core.exceptions import PermissionDenied
from django.conf.urls import url
from django.utils import translation
from django.http import HttpResponse
from django.db.models import Q

from .models import User
from alm_vcard.models import *
from alm_crm.models import SalesCycle, SalesCycleLogEntry, Contact, Category
from alm_user.models import Account
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )

from almanet.settings import DEFAULT_SERVICE, TIME_ZONE
from almanet.utils.api import RequestContext, CommonMeta
from almanet.utils.env import get_subscr_id
import json
import datetime
import ast



class OpenAuthEndpoint(Authentication):

    def is_authenticated(self, request, **kwargs):
        """
        Identifies if the user is authenticated to continue or not.
        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        auth_endpoint = '/api/v1/%s/auth%s' % (UserResource._meta.resource_name, trailing_slash())

        return request.path == auth_endpoint


# class UserSession(object):

#     @classmethod
#     def session_get_key(cls, request, create_if_needed=True):
#         if not request.session.session_key and create_if_needed:
#             request.session.create()
#         return request.session.session_key

#     @classmethod
#     def object_for_request(cls, request):
#         s = cls()
#         s.id = cls.session_get_key(request)
#         s.expire_date = request.session.get_expiry_date()
#         s.user = None

#         if request.user.is_authenticated():
#             s.user = request.user

#         return s


class UserResource(ModelResource):
    '''
    GET Method
    I{URL}:  U{alma.net:8000/api/v1/user/}

    B{Description}:
    API for User model

    @type  limit: number
    @param limit: The limit of results, 20 by default.
    @type  offset: number
    @param offset: The offset of results, 0 by default

    @return:  users

    >>> "objecs":[
    ... {
    ...     "email": "sattar94@outlook.com",
    ...     "first_name": "Sattar",
    ...     "id": 1,
    ...     "is_active": true,
    ...     "last_login": "2014-12-26T10:26:31.479259",
    ...     "last_name": "Stamkulov",
    ...     "resource_uri": "/api/v1/user/1/",
    ...     "timezone": "Asia/Almaty"
    ... },
    ... ]

    @undocumented: Meta
    '''
    vcard = fields.ToOneField('alm_vcard.api.VCardResource', 'vcard', null=True, full=True)

    class Meta(CommonMeta):
        queryset = User.objects.all()
        excludes = ['password', 'is_admin']
        list_allowed_methods = ['get', 'patch']
        detail_allowed_methods = ['get', 'patch']
        resource_name = 'user'

    def apply_filters(self, request, applicable_filters):
        user_ids = [acc.user_id for acc in request.company.accounts.all()]
        q = Q(id__in=user_ids)
        objects = super(ModelResource, self).apply_filters(request, applicable_filters)
        return objects.filter(q)

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/subscriptions%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('subscriptions'),
                name='api_subscriptions'
            ),
            url(
                r"^(?P<resource_name>%s)/current%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_current_user'),
                name='api_current_user'
            ),
            url(
                r"^(?P<resource_name>%s)/upload_userpic%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('upload_userpic'),
                name='api_upload_userpic'
            ),
            url(
                r"^(?P<resource_name>%s)/auth%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('authorization'),
                name='api_authorization'
            ),
            url(
                r"^(?P<resource_name>%s)/change_password%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('change_password'),
                name='api_change_password'
            ),
        ]

    def upload_userpic(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

            from django.core.files.uploadedfile import SimpleUploadedFile
            file_contents = SimpleUploadedFile("%s" %(data['name']), base64.b64decode(data['pic']), content_type='image')
            request.user.userpic.save(data['name'], file_contents, True)
            raise ImmediateHttpResponse(
                HttpResponse(
                    content=Serializer().to_json(
                        UserResource().full_dehydrate(
                            UserResource().build_bundle(
                                obj=User.objects.get(id=request.user.id))
                            )
                        ),
                    content_type='application/json; charset=utf-8', status=200)
            )

    def change_password(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
            old_password = data.get('old_password', None)
            new_password = data.get('new_password', None)
            user = request.user

            if old_password is None or new_password is None:
                self.error_response(request, {}, response_class=http.HttpBadRequest)

            print old_password, new_password
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return self.create_response(
                    request,
                    {
                        'success': True
                    }
                )
            else:
                return self.create_response(
                    request,
                    {
                        'success': False,
                        'error_message': "current password is incorrect"
                    }
                )
    # def dehydrate(self, bundle):
    #     subscription_id = get_subscr_id(bundle.request.user_env, DEFAULT_SERVICE)
    #     bundle.data['crm_user_id'] = bundle.obj.get_subscr_user(subscription_id=subscription_id).pk
    #     bundle.data['is_supervisor'] = bundle.obj.get_subscr_user(subscription_id=subscription_id).is_supervisor
    #     return bundle

    def get_current_user(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            bundle = self.build_bundle(obj=request.user, request=request)
            
            bundle.company = request.company
            bundle.session = {
                'user_id': request.user.id,
                'session_key': request.session.session_key
            }

            bundle = self.full_dehydrate(bundle)
            return self.create_response(request, bundle)

    def get_crm_subscription(self, request):
        user_env = request.user_env
        subscription_pk = None
        if 'subscriptions' in user_env:
            subscription_pk = filter(
                lambda x: user_env['subscription_{}'.format(x)]['slug'] == DEFAULT_SERVICE,
                user_env['subscriptions']
                )[0]
        return subscription_pk

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        if not bundle.obj or not self.get_bundle_detail_data(bundle):
            try:
                lookup_kwargs = self.lookup_kwargs_with_identifiers(bundle, kwargs)
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle=bundle, **lookup_kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        bundle = self.full_hydrate(bundle, **kwargs)
        #return self.save(bundle, skip_errors=skip_errors)
        raise ImmediateHttpResponse(
            HttpResponse(
                content=Serializer().to_json(
                    self.full_dehydrate(
                        self.build_bundle(
                            obj=User.objects.get(id=bundle.obj.id))
                        )
                    ),
                content_type='application/json; charset=utf-8', status=200
                )
            )
        return bundle

    def full_hydrate(self, bundle, **kwargs):
        user_id = kwargs.get('pk', None)
        if user_id:
            if bundle.data.get('vcard', ""):
                self.vcard_full_hydrate(bundle)
                bundle.obj.save()

        return bundle

    def full_dehydrate(self, bundle, for_list=False):
        bundle = super(self.__class__, self).full_dehydrate(bundle, for_list=True)
        bundle.data['unfollow_list'] = [contact.id for contact in bundle.obj.unfollow_list.all()]
        # TODO: use CustomFields with use_in_ids
        return bundle

    def vcard_full_hydrate(self, bundle):
        field_object = bundle.data.get('vcard',{})
        subscription_id = self.get_crm_subscription(bundle.request)
        if bundle.obj.vcard:
            vcard = bundle.obj.vcard
        else:
            vcard = VCard()
            vcard.save()
            vcard.user = bundle.obj
        vcard_fields = list(VCard._meta.get_fields_with_model())
        for vcard_field in vcard_fields:
            if vcard_field[0].__class__==models.fields.AutoField:
                pass
            elif vcard_field[0].__class__==models.fields.IntegerField:
                pass
            elif vcard_field[0].__class__==models.fields.DateField:
                attname = vcard_field[0].attname
                bday = field_object.get(attname, "")
                '''
                format = yyyy-mm-dd
                '''
                if bday:
                    bday = datetime.datetime.strptime(bday, '%Y-%m-%d').date()
                    vcard.__setattr__(attname, bday)
            elif vcard_field[0].__class__==models.fields.DateTimeField:
                attname = vcard_field[0].attname
                rev = field_object.get(attname, "")
                if rev:
                    rev = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
                    vcard.__setattr__(attname, bday)
            elif vcard_field[0].__class__==models.fields.CharField:
                attname = vcard_field[0].attname
                vcard.__setattr__(attname,
                    field_object.get(attname, ""))
        '''
        Now i need to go over the list of vcard keys
        check their model names, go through each and every
        model and check for three things
        1) if id is set, then change the values in json
        2) if id is not set, then create
        3) if models are missing then delete the missing values
        '''
        vcard_rel_fields = vcard._meta.get_all_related_objects()
        vcard_rel_fields.reverse()
        del vcard_rel_fields[0]
        del vcard_rel_fields[0]
        for vcard_field in vcard_rel_fields:
            field_value = vcard_field.var_name+'s'
            obj_list = ast.literal_eval(str(field_object.get(vcard_field.var_name+'s','None')))
            vcard_field_name = vcard_field.var_name+'_set'
            model = vcard.__getattribute__(vcard_field_name).model
            if obj_list:
                queryset = vcard.__getattribute__(vcard_field_name).all()
                json_objects = obj_list
                id_list = []
                for obj in json_objects:
                    if obj.get('id',None):
                        vcard_obj = model.objects.get(id=int(obj.get('id',None)))
                        vcard_obj.vcard = vcard
                        del obj['id']
                    else:
                        vcard_obj = model()
                        vcard_obj.vcard = vcard
                    for key, value in obj.viewitems():
                        if key=='vcard':
                            vcard_obj.vcard = VCard.objects.get(id=value)
                        else:
                            vcard_obj.__setattr__(key, value)
                    vcard_obj.subscription_id = subscription_id
                    vcard_obj.save()
                    id_list.append(vcard_obj.id)
                for obj in queryset:
                    if not obj.id in id_list:
                        obj.delete()
            else:
                for obj in model.objects.filter(vcard=vcard):
                    obj.delete()
        vcard.subscription_id = subscription_id
        vcard.save()

    def subscriptions(self, request, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net/api/v1/user/:id/subscriptions/}

        B{Description}:
        API function to return user's subscriptions

        @type  limit: number
        @param limit: The limit of results, 20 by default.
        @type  offset: number
        @param offset: The offset of results, 0 by default

        @return:  subscriptions by service name

        >>> {
        ...     "crm": {"id": 1, "is_active": true},
        ... }
        '''
        user_id = kwargs.get('id')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        user = User.objects.get(pk=user_id)
        return self.create_response(request, user.get_subscriptions(flat=True))


    def authorization(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['post']):
            data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

            user = authenticate(username=data.get('email'), password=data.get('password'))
            session_key = None
            session_expire_date = None
            if user is not None:
                if user.is_active:
                    login(request, user)  # will add session to request
                    session_key = request.session.session_key
                    session_expire_date = request.session.get_expiry_date()
                else:
                    data = {'message': "User is not activated"}
                    return self.error_response(request, data, response_class=http.HttpForbidden)
            else:
                data = {'message': "Invalid login"}
                return self.error_response(request, data, response_class=http.HttpUnauthorized)

            bundle = self.build_bundle(obj=None, data={
                'user': self.full_dehydrate(self.build_bundle(obj=request.user, request=request)),
                'session_key': session_key,
                'session_expire_date': session_expire_date
                }, request=request)
            return self.create_response(request, bundle)





class SessionObject(object):
    '''
    @undocumented: __init__, get_users, get_company(request), get_contacts,
    get_sales_cycles, get_activities, get_shares, get_constants,
    get_session
    '''

    def __init__(self, request=None):
        self.company = request.company
        self.user = request.user
        self.session = self.get_session(request)

    def get_session(self, request):
        return {
            'user_id': self.user.pk,
            'session_key': request.session.session_key,
            # 'logged_in': request.account.is_authenticated(),
            'language': translation.get_language(),
            'timezone': TIME_ZONE
        }


class SessionResource(Resource):

    session = fields.DictField(attribute='session', readonly=True)
    user = fields.DictField(readonly=True)
    company = fields.DictField(readonly=True)

    class Meta:
        resource_name = 'session_state'
        object_class = SessionObject
        authentication = MultiAuthentication(
            OpenAuthEndpoint(),
            # BasicAuthentication(),
            SessionAuthentication()
        )
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/current%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_current_state'),
                name='api_current_state'
            )]

    def dehydrate_user(self, bundle):
        user_bundle = UserResource().build_bundle(obj=bundle.obj.user)
        return UserResource().full_dehydrate(user_bundle)

    def dehydrate_company(self, bundle):
        company = bundle.obj.company
        return {
            'id': company.id,
            'name': company.name,
            'subdomain': company.subdomain
        }

    def get_current_state(self, request, **kwargs):
        with RequestContext(self, request, allowed_methods=['get']):
            bundle = self.build_bundle(obj=SessionObject(request=request), request=request)
            data = self.full_dehydrate(bundle)
            return self.create_response(request, data)



