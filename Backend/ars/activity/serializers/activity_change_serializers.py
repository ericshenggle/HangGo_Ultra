from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ars.models import *
from ars.activity_tag.serializers import *

import pytz
import math
time_format = "%Y/%m/%d %H:%M"
from ars.activity.serializers.other_serializers import User_act_Serializer

class Activity_Change_Serializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    activity_type = serializers.PrimaryKeyRelatedField(queryset=ActivityType.objects.all())

    create_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    attend_users = User_act_Serializer(many=True, read_only=True)
    # click_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'activity_type', 'start_enrollment_at', 
            'end_enrollment_at', 'location', 'position', 
            'latitude', 'longitude', 'public_status', 'audit_status',
            'photo', 'tags', 'create_user', 'attend_users' 
        ]
        read_only_fields = []
        # extra_kwargs = {
        #     'name': {'help_text': 'activity_name'},
        #     'activity_type': {'help_text': 'type'}
        # }

    def validate(self, attrs):
        if False:
            raise serializers.ValidationError("活动错误")
        return attrs
    
    def create(self, validated_data):
        # activity_type = activity_type.data
        tags_data = validated_data.pop('tags')
        # validated_data['create_user_id'] = 1
        activity = Activity.objects.create(**validated_data)
        # activity.activity_type = activity_type
        # for tag_id in tags_data:
        for tag in tags_data:
            activity.tags.add(tag)
        return activity

    # def update(self, instance, validated_data):
    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)
    #     activity = Activity.objects.get(id=instance.id)
    #     return activity       
    
class ActivityInfo_Change_Serializer(serializers.ModelSerializer):
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())
    
    class Meta:
        model = ActivityInfo
        fields = '__all__'


# class Lecture_Change_Serializer(serializers.ModelSerializer):
#     activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())
#     class Meta:
#         model = LectureInfo
#         fields = '__all__'

