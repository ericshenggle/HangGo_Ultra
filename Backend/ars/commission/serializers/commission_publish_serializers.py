from rest_framework import serializers

from ars.commission.serializers.other_serializers import User_Com_Serializer
from ars.models import *


class Commission_Publish_Serializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    commission_type = serializers.PrimaryKeyRelatedField(queryset=CommissionType.objects.all())

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    # click_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Commission
        fields = ['id', 'name', 'commission_type', 'start_time', 'end_time', 'create_time', 'real_time',
                  'user', 'location', 'status', 'description', 'audit', 'fee', 'tags']

    def save(self):
        # activity_type = activity_type.data
        tags_data = self.validated_data.pop('tags')
        # validated_data['create_user_id'] = 1
        commission = Commission.objects.create(**self.validated_data)
        # activity.activity_type = activity_type
        # for tag_id in tags_data:
        for tag in tags_data:
            commission.tags.add(tag)
        return commission
