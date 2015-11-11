import django_filters
from .models import Activity
from .serializers import ActivitySerializer
from rest_framework import filters
from rest_framework import generics

class ActivityFilter(django_filters.FilterSet):
    # id = django_filters.NumberFilter(lookup_type='lt')
    class Meta:
        model = Activity
        fields = {
        	'id':['lt','gt','exact'],
        }