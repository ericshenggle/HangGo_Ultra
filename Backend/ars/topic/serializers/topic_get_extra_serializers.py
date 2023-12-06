from rest_framework import serializers
from rest_framework import permissions, status
from rest_framework.response import Response
from ars.activity.serializers.activity_info_serializer import ActivityInfo_Serializer
from ars.models import *
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.other_serializers import User_act_Serializer
import math

from ars.topic.serializers.other_serializers import User_Topic_Serializer

time_format = "%Y/%m/%d %H:%M"
from datetime import *
from django.db.models import Count

class Topic_Type_act_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TopicType
        fields = ['id', 'name']

class Comment_top_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    comment_time = MyDateTimeField()
    class Meta:
        model = Topic_Comment
        fields = ['id', 'user',  'comment_content', 'comment_time','to_user','like']

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_Topic_Serializer(user)
        return serializer.data

    def get_to_user(self, instance):
        user_id = instance.to_user_id
        user = User.objects.get(id=user_id)
        serializer = User_Topic_Serializer(user)
        return serializer.data

    def get_like(self, obj):
        return obj.liked_topic_comment.all().count()

class Topic_Comment_Get_Serializer(serializers.ModelSerializer):
    topic_type = Topic_Type_act_Simple_Get_Serializer()

    comment = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    create_user = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()
    create_at = MyDateTimeField()

    class Meta:
        model = Topic
        fields = [
            'id', 'topic_type', 'name', 'create_at', 'audit', 'photo', 'description',
            'like', 'follow', 'create_user', 'comment'
        ]

    def get_create_user(self, instance):
        u_id = instance.create_user.id
        u = User.objects.get(id=u_id)
        s = User_act_Serializer(u)
        return s.data

    def get_photo(self, instance):
        # returning image url if there is an image else blank string
        return instance.photos.url if instance.photos else ''
    
    def get_comment(self, instance):
        comment = Topic_Comment.objects.filter(topic_id=instance.id)
        serializer = Comment_top_Serializer(comment, many=True)
        return serializer.data

    def get_follow(self, obj):
        return obj.sub_topic.all().count()

    def get_like(self, obj):
        return obj.liked_topic.all().count()