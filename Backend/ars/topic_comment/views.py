from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.models import *
from ars.comment.serializers import Comment_Serializer
from ars.notification.wxapi import send_comment_deleted
from ars.topic_comment.serializers import Topic_Comment_Serializer

from ars.utils import change_data_time_format
from ars.activity.act_util import MyDateTimeField
from datetime import datetime
DEBUG = False


act_id = openapi.Parameter('act_id', in_=openapi.IN_QUERY, description='年/月/日 小时/分钟',
                           type=openapi.TYPE_INTEGER)

comment_response = openapi.Response('comment', Comment_Serializer)


class Topic_Comment_Basic_View(APIView):
    @swagger_auto_schema(
        operation_summary='发送评论',
        operation_description=
        '''
        发送格式{
            'topic_id':,
            'at_user_id':, // 被@ 用户
            'comment':
        }
        具体可查看补充接口 评论
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={201: 'OK', 400: '评论错误', 401:'未授权'}
    )
    def post(self, resquest):
        user_id = resquest.user.id
        if DEBUG:
            user_id = 1
        elif user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data = resquest.data
        data['user_id'] = user_id
        # import pdb; pdb.set_trace()
        if 'to_user_id' not in data:
            data['to_user_id'] = 1
            user = User.objects.get(id=data['to_user_id'])
            topic = Topic.objects.get(id=data['topic_id'])
        else:
            try:
                user = User.objects.get(id=data['to_user_id'])
                topic = Topic.objects.get(id=data['topic_id'])
            except User.DoesNotExit:
                return Response({"error":"there"}, status=status.HTTP_404_NOT_FOUND)
        authority = user.authority
        if authority[1] == '0':
            return Response('当前用户无发布评论权限，请及时进行申诉', status=status.HTTP_400_BAD_REQUEST)

        if len(data['comment_content']) == 0:
            return Response('评论不能为空', status=status.HTTP_400_BAD_REQUEST)
        data['comment_time'] = datetime.now()
        topic_comment = Topic_Comment(**data)
        topic_comment.save()
        Notification(
            user=topic.create_user,
            not_type=Notification.NotificationType.评论回复,
            type=Notification.Type.话题,
            topic=topic,
            content="您在话题 " + topic.name + " 下收到了评论",
            isread=False
        ).save()
        if 'to_user_id' in data:
            Notification(
            user=user,
            not_type=Notification.NotificationType.评论回复,
            type=Notification.Type.话题,
            topic=topic,
            content="您在话题 " + topic.name + " 下的评论收到了回复",
            isread=False
        ).save()
        serializer = Topic_Comment_Serializer(topic_comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Topic_Comment_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据评论id得到单个评论',
        responses={200: comment_response}
    )
    def get(self, resquest, id):
        comment = Topic_Comment.objects.get(id=id)
        serializer = Topic_Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='删除评论',
        responses={204: 'OK', 401: '未授权', 403: '禁止', 404: '未找到该评论'}
    )
    def delete(self, request, id):
        if (not DEBUG) and not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            comment = Topic_Comment.objects.get(id=id)
            if (not DEBUG) and (not request.user.is_staff) and (comment.user != request.user):
                return Response(status=status.HTTP_403_FORBIDDEN)
            if (not DEBUG) and request.user.is_staff:
                Notification(
                    user=comment.user,
                    not_type=Notification.NotificationType.系统通知,
                    type=Notification.Type.话题,
                    topic=comment.topic,
                    content="您在话题 " + comment.topic.name + " 下的评论已经被管理员删除。",
                    isread=False
                ).save()
            comment.delete()
        except Topic_Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Comment_Top_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据话题id得到话题下所有评论',
        responses={201: comment_response}
    )
    def get(self, resquest, topic_id):
        comment = Topic_Comment.objects.filter(topic_id=topic_id)
        serializer = Topic_Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Topic_Comment_User_View(APIView):
    @swagger_auto_schema(
        operation_summary='得到用户所有话题评论',
        responses={201: comment_response}
    )
    def get(self, resquest):
        if DEBUG:
            user_id = 1
        else:
            user_id = resquest.user.id
        comment = Topic_Comment.objects.filter(user_id=user_id)
        serializer = Topic_Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Topic_Comment_ID_User_View(APIView):
    @swagger_auto_schema(
        operation_summary='得到指定id用户所有话题评论',
        responses={201: comment_response}
    )
    def get(self, resquest, id):
        user_id = id
        comment = Topic_Comment.objects.filter(user_id=user_id)
        serializer = Topic_Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
