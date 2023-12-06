from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ars.models import *
from ars.activity_tag.serializers import *

import pytz
import math

time_format = "%Y/%m/%d %H:%M"
from ars.activity.serializers.other_serializers import User_act_Serializer


class Topic_Change_Serializer(serializers.ModelSerializer):
    topic_type = serializers.PrimaryKeyRelatedField(queryset=TopicType.objects.all())

    create_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    # click_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = [
            'id', 'topic_type', 'name', 'create_at', 'audit', 'photos', 'description',
             'create_user'
        ]

    def validate(self, attrs):
        if False:
            raise serializers.ValidationError("活动错误")
        return attrs

    def create(self, validated_data):
        topic = Topic.objects.create(**validated_data)
        # activity.activity_type = activity_type
        # for tag_id in tags_data:
        return topic



class TopicInfo_Change_Serializer(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())

    class Meta:
        model = TopicInfo
        fields = '__all__'

