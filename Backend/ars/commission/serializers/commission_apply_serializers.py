from rest_framework import serializers

from ars.commission.com_util import MyDateTimeField
from ars.commission.serializers.commission_get_serializers import Commission_Get_Serializer
from ars.models import *


class Apply_Get_Serializer(serializers.ModelSerializer):
    commission = serializers.SerializerMethodField()
    apply_time = MyDateTimeField()

    class Meta:
        model = Commission_Accept
        fields = ['commission', 'apply_time']

    def get_commission(self, instance):
        commission_id = instance.commission.id
        commission = Commission.objects.get(id=commission_id)
        commission_serializers = Commission_Get_Serializer(instance=commission)
        return commission_serializers.data
