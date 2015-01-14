#!/usr/bin/python
# -*- coding: utf-8 -*-
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import Resource, ModelResource
from tastypie.exceptions import NotFound, BadRequest
from django.contrib.auth import login, logout, authenticate
from django.conf.urls import url
from tastypie.utils import trailing_slash
from alm_vcard.models import *
from alm_crm.models import Contact
from .models import User
from tastypie.authentication import (
    MultiAuthentication,
    SessionAuthentication,
    BasicAuthentication,
    )
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.http import HttpNotFound
from tastypie.serializers import Serializer
from django.http import HttpResponse
from almanet.settings import DEFAULT_SERVICE
import json
import datetime
import ast


class UserSession(object):

    @classmethod
    def session_get_key(cls, request, create_if_needed=True):
        if not request.session.session_key and create_if_needed:
            request.session.create()
        return request.session.session_key

    @classmethod
    def object_for_request(cls, request):
        s = cls()
        s.id = cls.session_get_key(request)
        s.expire_date = request.session.get_expiry_date()
        s.user = None

        if request.user.is_authenticated():
            s.user = request.user

        return s


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

    class Meta:
        queryset = User.objects.all()
        excludes = ['password', 'is_admin']
        list_allowed_methods = ['get', 'patch']
        detail_allowed_methods = ['get', 'patch']
        resource_name = 'user'
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication())
        authorization = Authorization()

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

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<id>\d+)/subscriptions%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('subscriptions'),
                name='api_subscriptions'
            )
        ]

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


class UserSessionResource(Resource):
    """
    GET Method
    I{URL}:  U{alma.net/api/v1/user_session}

    B{Description}:
    API resource to manage Session Authentication

    B{How to use with cURL}:

    I{Create session via email & password:}

    curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"email": "sattar94@outlook.com", "password": "qweasdzxc"}' http://alma.net:8000/api/v1/user_session/

    >>> HTTP/1.0 201 CREATED
    ... Date: Fri, 26 Dec 2014 03:58:09 GMT
    ... Server: WSGIServer/0.1 Python/2.7.6
    ... Access-Control-Allow-Headers: Content-Type,*
    ... Vary: Accept, Cookie
    ... Location: http://alma.net:8000/api/v1/user_session/3neickljn2s3hg9e6ahtysko0srm7umn/
    ... Access-Control-Allow-Credentials: true
    ... Access-Control-Allow-Origin: *
    ... Access-Control-Allow-Methods: POST,GET,OPTIONS,PUT,DELETE
    ... Content-Type: text/html; charset=utf-8
    ... Set-Cookie:  csrftoken=QU2hIAvkUxtnnncAf3nhOX7OvNy3W9fW; expires=Fri, 25-Dec-2015 03:58:08 GMT; Max-Age=31449600; Path=/
    ... Set-Cookie:  sessionid=3neickljn2s3hg9e6ahtysko0srm7umn; Domain=.alma.net; expires=Fri, 09-Jan-2015 03:58:08 GMT; httponly; Max-Age=1209600; Path=/

    I{Get information of created session via Cookie 'sessionid'}

    curl --dump-header - -H "Content-Type: application/json" -X GET -b "sessionid=3neickljn2s3hg9e6ahtysko0srm7umn" http://localhost:8000/api/v1/user_session/

    >>> {
    ... "meta": {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 1},
    ... "objects": [{
    ... "expire_date": "2015-01-09T04:12:55.022264",
    ... "id": "3neickljn2s3hg9e6ahtysko0srm7umn",
    ... "resource_uri": "/api/v1/user_session/3neickljn2s3hg9e6ahtysko0srm7umn/",
    ... "user": {
    ...     "id": 1,
    ...     "email": "sattar94@outlook.com",
    ...     "first_name": "Sattar",
    ...     "last_name": "Stamkulov",
    ...     "is_active": true,
    ...     "last_login": "2014-12-26T03:58:08.795864",
    ...     "resource_uri": "/api/v1/user/1/",
    ...     "timezone": "Asia/Almaty"
    ...     }
    ... }]
    ... }

    B{How to use via jQuery.AJAX}

    I{Create session via email & password:}

    >>> $.ajax({
    ...     url: 'api/v1/user_session/',
    ...     type: 'POST',
    ...     contentType: 'application/json',
    ...     data: '{"email":"sattar94@outlook.com", "password":"qweasdzxc"}'
    ... })

    @undocumented: Meta, get_resource_uri, get_object_list,
    _build_session_object, _build_session_object_or_raise,
    find_or_create_user_for_new_session
    """

    id = fields.CharField(attribute="id", readonly=True)
    expire_date = fields.DateTimeField(attribute="expire_date", readonly=True)
    user = fields.ForeignKey(UserResource, attribute="user", readonly=True,
                             full=True, null=True)

    class Meta:
        resource_name = 'user_session'
        object_class = UserSession
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        always_return_data = True

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name="api_dispatch_list"):
        if not bundle_or_obj:
            return super(UserSessionResource, self).get_resource_uri(
                bundle_or_obj, url_name)

        obj = bundle_or_obj
        if isinstance(obj, Bundle):
            obj = obj.obj

        kwargs = {
            "resource_name": self._meta.resource_name,
            "pk": obj.id
        }
        if self._meta.api_name:
            kwargs["api_name"] = self._meta.api_name

        url = self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)
        return url

    def get_object_list(self, request):
        l = []

        try:
            obj = self._build_session_object_or_raise(request)
            l.append(obj)
        except NotFound:
            pass

        return l

    def obj_get_list(self, bundle, **kwargs):
        '''
        GET METHOD
        I{URL}:  U{alma.net:8000/api/v1/user_session/}

        B{Description}:
        API function to get list of active session

        @return: HTTP status code back (201) and a Location header,
        which gives us the URI to our newly created resource.

        >>> {
        ... "objects": [{
        ...     "id": "ec30q2m7229il39ugk4aempehqyo5k1i",
        ...     "expire_date": "2014-12-08T11:49:43.298172",
        ...     "resource_uri": "/api/v1/user_session/ec30q2m7229il39ugk4aempehqyo5k1i/",
        ...     "user": {
        ...         "id": 1,
        ...         "resource_uri": "/api/v1/user/1/",
        ...         "last_name": "Wayne",
        ...         "first_name": "Bruce",
        ...         "email": "b.wayne@batman.bat",
        ...         "is_active": true,
        ...         "last_login": "2014-11-24T11:49:43.174099",
        ...         "timezone": "Asia/Almaty"
        ...     }
        ... }]
        ...}
        '''

        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        '''
        POST METHOD
        I{URL}:  U{alma.net:8000/api/v1/user_session/}

        B{Description}:
        API function to Create new user session (login)
        by the given user credentials: email, password.

        @type  email: string
        @param email: The email of user
        @type  password: string
        @param password: The password of user

        @return: HTTP status code back (201) and a Location header,
        which gives us the URI to our newly created resource.

        >>> HTTP/1.0 201 CREATED
        ... Date: Fri, 11 Nov 2014 06:48:36 GMT
        ... Server: WSGIServer/0.1 Python/2.7
        ... Content-Type: text/html; charset=utf-8
        ... Location: http://alma.net/api/v1/user_session/ec30q2m7229il39ugk4aempehqyo5k1i/
        '''

        user = self.find_or_create_user_for_new_session(bundle, **kwargs)
        if not user:
            raise NotFound("No user was found with your credentials.")
        login(bundle.request, user)

        bundle.obj = self._build_session_object(bundle.request)
        bundle = self.full_hydrate(bundle)
        return bundle

    def obj_delete(self, bundle, **kwargs):
        '''
        DELETE METHOD
        I{URL}:  U{alma.net:8000/api/v1/user_session/:id}

        B{Description}:
        API function to Delete session (logout)

        @type  id: string
        @param id: session id

        @return: response “Accepted” with HTTP status code 204

        >>> HTTP/1.0 204 NO CONTENT
        ... Date: Fri, 11 Nov 2014 06:48:36 GMT
        ... Server: WSGIServer/0.1 Python/2.7
        ... Content-Length: 0
        ... Content-Type: text/html; charset=utf-8
        '''

        self._build_session_object_or_raise(bundle.request, pk=kwargs["pk"])
        logout(bundle.request)

    def _build_session_object(self, request):
        return self._meta.object_class.object_for_request(request)

    def _build_session_object_or_raise(self, request, pk=None):
        key = self._meta.object_class.session_get_key(request,
                                                      create_if_needed=False)

        if not key:
            raise NotFound("Session could not be found for the request.")

        if pk and pk != key:
            raise NotFound("That's not your session.")

        return self._build_session_object(request)

    def find_or_create_user_for_new_session(self, bundle, **kwargs):
        return authenticate(**bundle.data)
