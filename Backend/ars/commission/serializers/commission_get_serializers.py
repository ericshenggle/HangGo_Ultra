from rest_framework import serializers

from ars.commission.com_util import MyDateTimeField
from ars.commission.serializers.other_serializers import User_Com_Serializer
from ars.models import *


class Commission_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionType
        fields = ['id', 'name']


class Tag_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class Commission_Get_Serializer(serializers.ModelSerializer):
    tags = Tag_Simple_Get_Serializer(many=True)
    commission_type = Commission_Type_Simple_Get_Serializer()
    start_time = MyDateTimeField()
    end_time = MyDateTimeField()
    create_time = MyDateTimeField()

    user = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = ['id', 'name', 'commission_type', 'start_time', 'end_time', 'create_time', 'real_time',
                  'user', 'location', 'status', 'description', 'audit', 'fee', 'tags']

    def get_user(self, instance):
        u_id = instance.user.id
        u = User.objects.get(id=u_id)
        s = User_Com_Serializer(u)
        return s.data


