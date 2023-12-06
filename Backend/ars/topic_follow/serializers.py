from rest_framework import serializers
from ars.models import *
from ars.utils import code2session
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.activity.serializers.other_serializers import User_act_Serializer
time_format = "%Y/%m/%d %H:%M"

class Topic_Follow_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    

    class Meta:
        model = Topic_Subscribe
        fields = '__all__'

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_topic(self, instance):
        topic = Topic.objects.get(id=instance.topic_id)
        return {'id':topic.id, 'name':topic.name}