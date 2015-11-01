from contextlib import contextmanager
from django.middleware.csrf import _sanitize_token, constant_time_compare
from tastypie.authentication import Authentication, MultiAuthentication, ApiKeyAuthentication, BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from alm_user.models import Account, User
from almanet import settings


@contextmanager
def RequestContext(resource, request, auth=True, allowed_methods=None):
    """Managers lifecycle of tastypie api request"""
    allowed_methods = allowed_methods or []
    resource.method_check(request, allowed=allowed_methods)
    if auth:
    	resource.is_authenticated(request)
    resource.throttle_check(request)
    yield
    resource.log_throttled_access(request)


class ApiKeyAuthentication(ApiKeyAuthentication):

    def get_key(self, user, api_key):
        """
        Attempts to find the API key for the user. Uses ``ApiKey`` by default
        but can be overridden.
        """

        try:
            Account.objects.get(user=user, key=api_key)
        except Account.DoesNotExist:
            return self._unauthorized()

        return True


class SessionAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):

        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return request.user.is_authenticated()

        if getattr(request, '_dont_enforce_csrf_checks', False):
            return request.user.is_authenticated()

        csrf_token = _sanitize_token(request.COOKIES.get(settings.CSRF_COOKIE_NAME, ''))

        if request.is_secure():
            referer = request.META.get('HTTP_REFERER')

            if referer is None:
                return False

            good_referer = 'https://%s/' % request.get_host()

            if not same_origin(referer, good_referer):
                return False

        request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            return False

        return request.user.is_authenticated()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """

        return getattr(request.user, User.USERNAME_FIELD)



class DummyPaginator(object):
    def __init__(self, request_data, objects, resource_uri=None,
                 limit=None, offset=0, max_limit=1000,
                 collection_name='objects'):
        self.objects = objects
        self.collection_name = collection_name

    def page(self):
        return {self.collection_name: self.objects}


class CommonMeta:
    list_allowed_methods = ['get', 'post', 'patch']
    detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
    authentication = MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication(), BasicAuthentication())
    authorization = Authorization()

    if not settings.RUSTEM_SETTINGS:
        paginator_class = DummyPaginator

    filtering = {
        'date_edited': ALL_WITH_RELATIONS
    }



class CustomToManyField(fields.ToManyField):
    """
    used to add 'full_use_ids' flag for return objects 'ids' not 'resource_uri'
    GET & POST array of ids to object with ManyToMany relation
    """
    def __init__(self, to, attribute, related_name=None, default=None,
                 null=False, blank=False, readonly=False, full=False,
                 unique=False, help_text=None, use_in='all', full_list=True, full_detail=True,

                 full_use_ids=False
                 ):

        super(self.__class__, self).__init__(
            to, attribute, related_name=related_name, default=default,
            null=null, blank=blank, readonly=readonly, full=full,
            unique=unique, help_text=help_text, use_in=use_in,
            full_list=full_list, full_detail=full_detail
        )

        self.full_use_ids = full_use_ids


    def dehydrate_related(self, bundle, related_resource, for_list=True):
        """
        Based on the ``full_resource``, returns either the endpoint or the data
        from ``full_dehydrate`` for the related resource.

        CUSTOM:
            return 'id' as endpoint if full_use_ids
        """

        if self.full_use_ids:
            return related_resource.get_resource_id(bundle)
        else:
            return super(self.__class__, self).dehydrate_related(bundle, related_resource, for_list=for_list)


    def build_related_resource(self, value, request=None, related_obj=None, related_name=None):
        obj_id = value
        kwargs = {
            'request': request,
            'related_obj': related_obj,
            'related_name': related_name,
        }
        self.fk_resource = self.to_class()
        bundle = self.fk_resource.build_bundle(obj={'pk': obj_id}, request=request)
        obj = self.fk_resource.obj_get(bundle, pk=obj_id)
        return self.resource_from_pk(self.fk_resource, obj, **kwargs)



def use_in_field(field_name):
    '''
        tastypie's 'use_in' keywarg used for:
             Optionally accepts ``use_in``. This may be one of ``list``, ``detail``
            ``all``
            or
            a callable which accepts a ``bundle`` and returns
            ``True`` or ``False``. Indicates wheather this field will be included
            during dehydration of a list of objects or a single object. If ``use_in``
            is a callable, and returns ``True``, the field will be included during
            dehydration.
            Defaults to ``all``.

        Example:
            see MobileStateResource, where passed to skip 'activities' in SalesCycles
            see SalesCycleResource, 'activities' CustomToManyField with this function
    '''
    def use_in(bundle):
        if hasattr(bundle, 'use_fields'):
            if field_name in getattr(bundle, 'use_fields'):
                return True
        return False
    return use_in


def skip_in_field(field_name):
    '''
        works as use_in_field but opposite
    '''
    def use_in(bundle):
        if hasattr(bundle, 'skip_fields'):
            if field_name in getattr(bundle, 'skip_fields'):
                return False
        return True
    return use_in



def firstOfQuerySet(queryset):
    try :
        return queryset.all()[0]
    except IndexError:
        return None
