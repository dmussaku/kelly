import django_filters

from django_filters import MethodFilter
from django.db.models import Q

from rest_framework import filters, generics

from alm_crm.models import (
    Activity, 
    Contact,
    ContactList,
    SalesCycle,
    Share,
 )
# from .serializers import (
#     ActivitySerializer,
#     ContactSerializer
#     )

class ActivityFilter(django_filters.FilterSet):
    search = MethodFilter()
    class Meta:
        model = Activity

    def filter_search(self, queryset, value):
        queryset = queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
            )
        return queryset.distinct()

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
            Q(vcard__emails__value__icontains=value) |
            Q(vcard__titles__data__icontains=value) | 
            Q(vcard__urls__value__icontains=value) | 
            Q(vcard__adrs__country_name__icontains=value) | 
            Q(vcard__adrs__locality__icontains=value) | 
            Q(vcard__adrs__postal_code__icontains=value) | 
            Q(vcard__adrs__region__icontains=value) | 
            Q(vcard__adrs__street_address__icontains=value) | 
            Q(vcard__notes__data__icontains=value) 
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


class SalesCycleFilter(django_filters.FilterSet):
    search = MethodFilter()

    class Meta:
        model = SalesCycle

    def filter_search(self, queryset, value):
        queryset = queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
            )
        return queryset.distinct()


class ShareFilter(django_filters.FilterSet):
    search = MethodFilter()

    class Meta:
        model = Share

    
    def filter_search(self, queryset, value):
        queryset = queryset.filter(
            Q(note__icontains=value)
            )
        return queryset.distinct()
