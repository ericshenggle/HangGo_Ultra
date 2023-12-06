from rest_framework import serializers
from ars.models import *
from ars.commission.com_util import MyDateTimeField
from ars.commission.serializers.other_serializers import User_Com_Serializer

time_format = "%Y/%m/%d %H:%M"


class Commission_Comment_Reply_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    to_comment_id = serializers.SerializerMethodField()
    comment_time = MyDateTimeField()

    class Meta:
        model = Commission_Comment_Reply
        fields = ['id', 'user', 'to_user', 'comment_time', 'comment', 'to_comment_id']

    def get_to_user(self, instance):
        user_id = instance.to_user_id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
        serializer = User_Com_Serializer(user)
        return serializer.data
    
    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_Com_Serializer(user)
        return serializer.data

    def get_to_comment(self, instance):
        return instance.to_comment_id
    

class Commission_Comment_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    commission = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    comment_time = MyDateTimeField()

    class Meta:
        model = Commission_Comment
        fields = ['id', 'user', 'commission', 'comment_time', 'comment', 'reply']

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_Com_Serializer(user)
        return serializer.data

    def get_commission(self, instance):
        commission = Commission.objects.get(id=instance.commission_id)
        return {'id': commission.id, 'name': commission.name}

    def get_reply(self, instance):
        reply_list = instance.user_commission_reply_at.all()
        serializer = Commission_Comment_Reply_Serializer(instance=reply_list, many=True)
        return serializer.data
