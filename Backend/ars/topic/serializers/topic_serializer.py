from rest_framework import serializers
from ars.user.serializers import UserSerializer
from ars.models import *
from ars.activity_tag.serializers.tag_serializers import Tag_Serializer
from ars.activity_type.serializers.type_serializers import Activity_Type_Serializer

class Topic_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TopicType
        fields = ['id', 'name']

class Topic_Serializer(serializers.ModelSerializer):
    topic_type = Topic_Type_Simple_Get_Serializer()
    class Meta:
        model = Topic
        fields = [
            'id', 'topic_type', 'name',
            'create_at', 'create_user',
            'description', 'audit', 'photos',
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
        instance.audit = validated_data['audit']
        instance.save()
        # 2,返回数据
        topic = Topic.objects.get(id=instance.id)
        return topic






