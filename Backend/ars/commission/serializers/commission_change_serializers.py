from rest_framework import serializers
from ars.user.serializers import UserSerializer
from ars.models import *
from ars.activity_tag.serializers.tag_serializers import Tag_Serializer
from ars.activity_type.serializers.type_serializers import Activity_Type_Serializer


class Commission_Change_Serializer(serializers.ModelSerializer):
    commission_type = serializers.PrimaryKeyRelatedField(queryset=CommissionType.objects.all())

    class Meta:
        model = Commission
        fields = ['id', 'name', 'commission_type', 'start_time', 'end_time', 'create_time', 'real_time',
                  'location', 'status', 'description', 'audit', 'fee']

    def update(self, instance, validated_data):
        # new
        # print(validated_data)
        instance.name = validated_data["name"]
        instance.commission_type_id = validated_data['commission_type']
        instance.start_time = validated_data['start_time']
        instance.end_time = validated_data['end_time']
        instance.location = validated_data['location']
        instance.status = validated_data['status']
        instance.real_time = validated_data['real_time']
        if instance.audit == Commission.AuditStatusChoice.审核失败:
            instance.audit = Commission.AuditStatusChoice.审核通过
        else:
            instance.audit = validated_data['audit']
        instance.fee = validated_data['fee']
        instance.description = validated_data['description']
        instance.save()
        # 2,返回数据
        commission = Commission.objects.get(id=instance.id)
        return commission






