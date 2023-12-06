from rest_framework import serializers
from ars.models import *
from ars.utils import code2session
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.activity.serializers.other_serializers import User_act_Serializer
time_format = "%Y/%m/%d %H:%M"

class Comment_Serializer(serializers.ModelSerializer):
    at_user = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()
    comment_time = MyDateTimeField()
    

    class Meta:
        model = Comment
        fields = '__all__'

    def get_at_user(self, instance):
        user_id = instance.at_user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_activity(self, instance):
        activity = Activity.objects.get(id=instance.activity_id)
        return {'id':activity.id, 'name':activity.name}