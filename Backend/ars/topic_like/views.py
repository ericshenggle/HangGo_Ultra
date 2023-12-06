from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.models import *
from ars.comment.serializers import Comment_Serializer
from ars.notification.wxapi import send_comment_deleted
from ars.topic_follow.serializers import Topic_Follow_Serializer
from ars.topic_like.serializers import Topic_Like_Serializer

from ars.utils import change_data_time_format
from ars.activity.act_util import MyDateTimeField
from datetime import datetime
DEBUG = False


act_id = openapi.Parameter('act_id', in_=openapi.IN_QUERY, description='年/月/日 小时/分钟',
                           type=openapi.TYPE_INTEGER)

comment_response = openapi.Response('comment', Topic_Follow_Serializer)



class Topic_Like_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据话题id得到所有的点赞者',
        responses={200: 'OK'}
    )
    def get(self, resquest, id):
        users = Topic_Like.objects.filter(topic_id= id)
        serializer = Topic_Like_Serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='取消点赞',
        responses={204: 'OK'}
    )
    def delete(self, request, id):
        if (not DEBUG) and not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = 1 if DEBUG else request.user.id
            follow = Topic_Like.objects.get(topic_id=id, user_id = user_id)
            if (not DEBUG) and (not request.user.is_staff) and (follow.user != request.user):
                return Response(status=status.HTTP_403_FORBIDDEN)
            if follow:
                follow.delete()
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Topic_Like.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Topic_Like_User_View_Self(APIView):
    @swagger_auto_schema(
        operation_summary='得到用户所有点赞话题',
        responses={201: comment_response}
    )
    def get(self, resquest):
        if DEBUG:
            user_id = 1
        else:
            user_id = resquest.user.id
        subs = Topic_Like.objects.filter(user_id=user_id)
        serializer = Topic_Like_Serializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Topic_Like_User_View(APIView):
    @swagger_auto_schema(
        operation_summary='得到指定用户所有话题点赞',
        responses={201: comment_response}
    )
    def get(self, resquest, id):
        user_id = id
        subs = Topic_Like.objects.filter(user_id=user_id)
        serializer = Topic_Like_Serializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Topic_Like_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='点赞话题',
        operation_description=
        '''
        发送格式{
            'activity_id':,
            'topic_id':
        }
        具体可查看补充接口 评论
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={201: 'OK', 400: '关注错误'}
    )
    def post(self, resquest):
        user_id = resquest.user.id
        if DEBUG:
            user_id = 1
        elif user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data = resquest.data
        data['user_id'] = user_id
        try:
            topic = Topic.objects.get(id=data['topic_id'])
        except Topic.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        tf = Topic_Like.objects.filter(topic_id=data['topic_id'], user_id=data['user_id'])
        if tf:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        topic_follow = Topic_Like(**data)
        topic_follow.save()
        serializer = Topic_Like_Serializer(topic_follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



