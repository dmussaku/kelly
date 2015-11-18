import django_filters

from django_filters import MethodFilter
from django.db.models import Q

from rest_framework import filters, generics

from alm_crm.models import (
    Activity, 
    Contact,
    ContactList,
 )
# from .serializers import (
#     ActivitySerializer,
#     ContactSerializer
#     )

class ActivityFilter(django_filters.FilterSet):
    # id = django_filters.NumberFilter(lookup_type='lt')
    class Meta:
        model = Activity
        fields = {
            'id':['lt','gt','exact'],
        }

class ContactFilter(django_filters.FilterSet):
    search = MethodFilter()
    contact_list_id = MethodFilter()
    vcard__emails__value = MethodFilter()
    vcard__tels__value = MethodFilter()
    tp = MethodFilter()

    class Meta:
        model = Contact
        fields = {
            'tp':['exact'],
        }


    def filter_search(self, queryset, value):
        queryset = queryset.filter(
            Q(vcard__fn__icontains=value) |
            Q(vcard__given_name__icontains=value) |
            Q(vcard__family_name__icontains=value) |
            Q(vcard__tels__value__icontains=value) |
            Q(vcard__emails__value__icontains=value) 
            )
        return queryset.distinct()

    def filter_vcard__emails__value(self, queryset, value):
        queryset = queryset.filter(vcard__emails__value__icontains=value)
        return queryset

    def filter_vcard__tels__value(self, queryset, value):
        queryset = queryset.filter(vcard__tels__value__icontains=value)
        return queryset

    def filter_tp(search, queryset, value):
        if value=='all':
            return queryset
        else:
            return queryset.filter(tp=value)

    def filter_contact_list_id(self, queryset, value):
        queryset = queryset.filter(contact_list__id=value)
        return queryset
