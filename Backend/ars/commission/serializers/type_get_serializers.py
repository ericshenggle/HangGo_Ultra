from rest_framework import serializers

from ars.commission.serializers.commission_get_serializers import Commission_Get_Serializer
from ars.models import *
from datetime import *


class Commission_Type_Get_Serializer(serializers.ModelSerializer):
    commissions = serializers.SerializerMethodField()

    class Meta:
        model = CommissionType
        fields = '__all__'

    def get_commissions(self, instance):
        td = timedelta(days=100)
        now = datetime.now()
        commissions = instance.type_commissions.filter(audit=Commission.AuditStatusChoice.审核通过, 
                    status=Commission.PublicStatusChoice.已发布, end_time__range=(now, now + td)).order_by('-create_time')
        commissions_serializers = Commission_Get_Serializer(instance=commissions, many=True)
        return commissions_serializers.data


class Commission_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CommissionType
        fields = ['id', 'name', 'image']

    def get_image(self, instance):
        return instance.image.url if instance.image else ''
