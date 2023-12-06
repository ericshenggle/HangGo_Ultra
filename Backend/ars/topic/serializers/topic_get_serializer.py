from rest_framework import serializers

from ars.activity.serializers.activity_info_serializer import ActivityInfo_Serializer
# from ars.activity.serializers.lecture_serializer import Lecture_Serializer
from ars.activity.serializers.other_serializers import User_act_Serializer
from ars.models import *
from ars.activity.act_util import *
import math
from datetime import *
from django.db.models import Count


class Topic_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TopicType
        fields = ['id', 'name']



class Topic_Get_Serializer(serializers.ModelSerializer):
    topic_type = Topic_Type_Simple_Get_Serializer()

    # normal_activity = ActivityInfo_Serializer(read_only=True)
    # lecture = Lecture_Serializer(read_only=True)
    # normal_activity = serializers.SerializerMethodField()
    # lecture = serializers.SerializerMethodField()
    create_at = MyDateTimeField()

    photo = serializers.SerializerMethodField()
    create_user = serializers.SerializerMethodField()

    like = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'topic_type', 'name', 'create_at',
             'audit', 'photo', 'description',
            'like', 'follow', 'create_user'
        ]


    def get_photo(self, instance):
        # returning image url if there is an image else blank string
        return instance.photos.url if instance.photos else ''

    def get_create_user(self, instance):
        u_id = instance.create_user.id
        u = User.objects.get(id=u_id)
        s = User_act_Serializer(u)
        return s.data

    def get_follow(self, obj):
        return obj.sub_topic.all().count()

    def get_like(self, obj):
        return obj.liked_topic.all().count()