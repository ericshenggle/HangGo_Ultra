from rest_framework import serializers
from ars.models import *
from ars.utils import code2session
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.activity.serializers.other_serializers import User_act_Serializer
from ars.topic.serializers.topic_serializer import Topic_Serializer
time_format = "%Y/%m/%d %H:%M"

class Topic_Click_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    click_time = MyDateTimeField()

    class Meta:
        model = ClickRecord_Topic
        fields = ['user', 'topic', 'click_time']

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_topic(self, instance):
        topic = Topic.objects.get(id=instance.topic_id)
        serializer = Topic_Serializer(topic)
        return serializer.data

