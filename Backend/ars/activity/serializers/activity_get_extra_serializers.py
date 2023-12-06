from rest_framework import serializers
from rest_framework import permissions, status
from rest_framework.response import Response
from ars.activity.serializers.activity_info_serializer import ActivityInfo_Serializer
from ars.models import *
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.other_serializers import User_act_Serializer
import math
time_format = "%Y/%m/%d %H:%M"
from datetime import *
from django.db.models import Count

class Activity_Type_act_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = ['id', 'name']

class Tag_Simple_act_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']    

class Comment_act_Serializer(serializers.ModelSerializer):
    at_user = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'at_user', 'comment']

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

class Activity_Comment_Get_Serializer(serializers.ModelSerializer):
    tags = Tag_Simple_act_Get_Serializer(many=True)
    activity_type = Activity_Type_act_Simple_Get_Serializer()

    normal_activity = serializers.SerializerMethodField()
    start_enrollment_at = MyDateTimeField()
    end_enrollment_at = MyDateTimeField()
    comment = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    create_user = serializers.SerializerMethodField()
    heat = serializers.SerializerMethodField()
    remark = serializers.SerializerMethodField()
    attend_users =serializers.SerializerMethodField()
    attend_user_num = serializers.SerializerMethodField()

    class Meta:
        model = Activity 
        fields = [
            'id', 'name', 'activity_type', 'start_enrollment_at', 
            'end_enrollment_at', 'location', 'position', 
            'latitude', 'longitude', 'public_status', 'audit_status',
            'photo', 'tags', 'create_user', 'attend_users', 'comment', 
            'normal_activity', 'heat', 'remark', 'attend_user_num'
        ]

        read_only_fields = [
            'create_user', 'attend_users', 'attend_user_num'
        ]

    def get_attend_user_num(self, instance):
        if instance.activity_type_id == 9:
            # if instance.bykc_has_attend_number is None:
            #     return instance.normal_activity.all()[0].allow_total
            return instance.bykc_has_attend_number
        else:
            return len(instance.attend_users.all())

    def get_heat(self, instance):
        now = datetime.now()
        td = timedelta(days=10)
        if 'start' in self.context:
            start = self.context['start']
        else:
            start = now - td
        if 'end' in self.context:
            end = self.context['end']
        else:
            end = now + td
        click_record = ClickRecord.objects.filter(click_time__range=(start, end))
        activities = click_record.filter(activity_id=instance.id)
        
        num = len(activities)
        heat_score = math.exp(num/100)
        heat_score = max(min(3, heat_score), 0)
        return int(heat_score)

    def get_remark(self, instance):
        user = self.context.get('user')
        if user.id is None or user.id == 1:
            return 0
        try:
            user_act = UserActivity.objects.get(user=user, activity=instance)
        except UserActivity.DoesNotExist:
            return 0
        return user_act.remark

    def get_create_user(self, instance):
        u_id = instance.create_user.id
        u = User.objects.get(id=u_id)
        s = User_act_Serializer(u)
        return s.data

    def get_attend_users(self, instance):
        us = instance.attend_users
        s = User_act_Serializer(us, many=True)
        return s.data

    def get_photo(self, instance):
        # returning image url if there is an image else blank string
        return instance.photo.url if instance.photo else ''
    
    def get_normal_activity(self, obj):
        if len(obj.normal_activity.all()) == 0:
            return []
        normal_activity = obj.normal_activity.all().first()
        normal_activity_serializer = ActivityInfo_Serializer(instance=normal_activity)
        return normal_activity_serializer.data
    
    def get_comment(self, instance):
        comment = Comment.objects.filter(activity_id=instance.id)
        serializer = Comment_act_Serializer(comment, many=True)
        return serializer.data