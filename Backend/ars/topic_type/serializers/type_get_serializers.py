from rest_framework import serializers

from ars.models import ActivityType, TopicType
from ars.activity.serializers.other_serializers import User_act_Serializer
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.topic.serializers.topic_get_serializer import Topic_Get_Serializer


class Topic_Type_Get_Serializer(serializers.ModelSerializer):
    # subscribe_users = UserSerializer(many=True, read_only=True)
    # type_activities = Activity_Get_Serializer()
    type_topics = serializers.SerializerMethodField()

    # type_activities = serializers.PrimaryKeyRelatedField(queryset=ActivityType.objects.all())

    class Meta:
        model = TopicType
        fields = '__all__'

    def get_type_topics(self, obj):
        # if len(obj.type_activities.all()) == 0:
        #     return {}
        type_activities = obj.type_topics.all()
        type_activities_serializers = Topic_Get_Serializer(instance=type_activities, many=True)
        return type_activities_serializers.data


class Topic_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TopicType
        fields = ['id', 'name', 'image']
