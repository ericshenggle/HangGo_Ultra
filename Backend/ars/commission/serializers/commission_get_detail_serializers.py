from rest_framework import serializers

from ars.commission.com_util import MyDateTimeField
from ars.commission.serializers.other_serializers import User_Com_Serializer
from ars.models import *


class Commission_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionType
        fields = ['id', 'name']


class Tag_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

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

class Commission_Com_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    comment_time = MyDateTimeField()

    class Meta:
        model = Commission_Comment
        fields = ['id', 'user', 'comment_time', 'comment', 'reply']

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_Com_Serializer(user)
        return serializer.data

    def get_reply(self, instance):
        reply_list = instance.user_commission_reply_at.all()
        serializer = Commission_Comment_Reply_Serializer(instance=reply_list, many=True)
        return serializer.data


class Commission_Get_Detail_Serializer(serializers.ModelSerializer):
    tags = Tag_Simple_Get_Serializer(many=True)
    commission_type = Commission_Type_Simple_Get_Serializer()
    start_time = MyDateTimeField()
    end_time = MyDateTimeField()
    create_time = MyDateTimeField()

    user = serializers.SerializerMethodField()
    accepted_user = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = ['id', 'name', 'commission_type', 'start_time', 'end_time', 'create_time', 'real_time',
                  'user', 'location', 'status', 'description', 'audit', 'fee', 'tags', 'comment', 'score', 'accepted_user']

    def get_user(self, instance):
        u_id = instance.user.id
        u = User.objects.get(id=u_id)
        s = User_Com_Serializer(u)
        return s.data

    def get_comment(self, instance):
        comment = Commission_Comment.objects.filter(commission_id=instance.id)
        serializer = Commission_Com_Serializer(comment, many=True)
        return serializer.data

    def get_score(self, instance):
        try:
            score = UserCommission.objects.get(commission=instance)
        except UserCommission.DoesNotExist:
            return 0
        return score.score

    def get_accepted_user(self, instance):
        try:
            accept = Commission_Accept.objects.get(commission=instance)
        except Commission_Accept.DoesNotExist:
            return
        serializer = User_Com_Serializer(accept.user)
        return serializer.data

