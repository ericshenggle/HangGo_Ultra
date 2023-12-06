from django.core import serializers
from django.db.models import Count
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.models import *
from ars.comment.serializers import Comment_Serializer
from ars.notification.wxapi import send_comment_deleted
from ars.topic_click.serializers import Topic_Click_Serializer


from ars.utils import change_data_time_format
from ars.activity.act_util import MyDateTimeField
from datetime import datetime
DEBUG = False


act_id = openapi.Parameter('act_id', in_=openapi.IN_QUERY, description='年/月/日 小时/分钟',
                           type=openapi.TYPE_INTEGER)



class Topic_Click_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据话题id得到所有的点击者',
        responses={200: 'OK'}
    )
    def get(self, resquest, id):
        users = ClickRecord_Topic.objects.filter(topic_id = id).order_by('-click_time')
        serializer = Topic_Click_Serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Topic_Click_User_View_Self(APIView):
    @swagger_auto_schema(
        operation_summary='得到用户所有点击话题',
    )
    def get(self, resquest):
        if DEBUG:
            user_id = 1
        else:
            user_id = resquest.user.id
        subs = ClickRecord_Topic.objects.filter(user_id=user_id).order_by('-click_time')
        serializer = Topic_Click_Serializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Topic_Click_User_View(APIView):
    @swagger_auto_schema(
        operation_summary='得到指定用户所有话题点赞',
    )
    def get(self, resquest, id):
        user_id = id
        subs = ClickRecord_Topic.objects.filter(user_id=user_id).order_by('-click_time')
        serializer = Topic_Click_Serializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Topic_Click_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据点击量排序获取热门话题',
        responses={201: 'OK'}
    )
    def get(self, resquest):
        hotTopic = ClickRecord_Topic.objects.values('topic_id').annotate(count=Count('topic_id')).order_by("-count")
        province = list(hotTopic)

        return Response(province, status=status.HTTP_201_CREATED)



