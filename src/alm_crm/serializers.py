from rest_framework import serializers

from alm_crm.models import Milestone

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
