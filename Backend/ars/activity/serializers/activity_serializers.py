from rest_framework import serializers
from ars.user.serializers import UserSerializer
from ars.models import *
from ars.activity_tag.serializers.tag_serializers import Tag_Serializer
from ars.activity_type.serializers.type_serializers import Activity_Type_Serializer


class Activity_Serializer(serializers.ModelSerializer):
    activity_type = serializers.PrimaryKeyRelatedField(queryset=ActivityType.objects.all())

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'start_enrollment_at', 
            'end_enrollment_at', 'location', 'position', 
            'latitude', 'longitude', 'audit_status',
            'attend_users', 'activity_type'
        ]
        # read_only_fields = ['tags', 'activity_type']
        # extra_kwargs = {
        #     'name': {'help_text': 'activity_name'},
        #     'activity_type': {'help_text': 'type'}
        # }

    def validate(self, attrs):
        if False:
            raise serializers.ValidationError("活动错误")
        return attrs

    '''
    def create(self, validated_data):
        import pdb; pdb.set_trace()
        tags = validated_data.pop('tags')
        type_data = dict(validated_data.pop('activity_type'))
        activity_type = Activity_Type_Serializer(data=type_data)

        pdb.set_trace()
        if activity_type.is_valid():
            activity_type.save()
            # activity_type = activity_type.data
        activity = Activity.objects.create(activity_type=activity_type,**validated_data)
        # activity.activity_type = activity_type

        for tag_data in tags:
            tag_data = dict(tag_data)
            tag = Tag_Serializer(data=tag_data)
            if tag.is_valid(raise_exception=True):
                tag.save()
                tag = tag.data
            activity.tags.add(tags)
        activity.save()
        return activity
    '''

    def update(self, instance, validated_data):
        # new 
        # print(validated_data)
        instance.name = validated_data["name"]
        # instance.activity_type = validated_data['activity_type']
        instance.start_enrollment_at = validated_data['start_enrollment_at']
        instance.end_enrollment_at = validated_data['end_enrollment_at']
        instance.location = validated_data['location']
        instance.audit_status = validated_data['audit_status']
        instance.position = validated_data['position']
        
        if 'latitude' in validated_data:
            instance.latitude = validated_data['latitude']
        else:
            instance.latitude = None
        if 'longitude' in validated_data:
            instance.longitude = validated_data['longitude']
        else:
            instance.longitude = None
        instance.activity_type = validated_data['activity_type']
        # if 'photo' in validated_data:
        #     instance.photo = validated_data['photo']
        instance.audit_status = validated_data['audit_status']
        instance.save()
        # 2,返回数据
        activity = Activity.objects.get(id=instance.id)
        return activity






