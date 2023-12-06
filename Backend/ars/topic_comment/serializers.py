from rest_framework import serializers
from ars.models import *
from ars.utils import code2session
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.activity.serializers.other_serializers import User_act_Serializer
time_format = "%Y/%m/%d %H:%M"

class Topic_Comment_Serializer(serializers.ModelSerializer):
    to_user = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    comment_time = MyDateTimeField()
    like = serializers.SerializerMethodField()
    

    class Meta:
        model = Topic_Comment
        fields = '__all__'

    def get_to_user(self, instance):
        user_id = instance.to_user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_topic(self, instance):
        topic = Topic.objects.get(id=instance.topic_id)
        return {'id':topic.id, 'name':topic.name}

    def get_like(self, obj):
        return obj.liked_topic_comment.all().count()