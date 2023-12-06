from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.models import *
from ars.comment.serializers import Comment_Serializer
from ars.notification.wxapi import send_comment_deleted

from ars.utils import change_data_time_format
from ars.activity.act_util import MyDateTimeField
from datetime import datetime

act_id = openapi.Parameter('act_id', in_=openapi.IN_QUERY, description='年/月/日 小时/分钟',
                           type=openapi.TYPE_INTEGER)

comment_response = openapi.Response('comment', Comment_Serializer)


class Comment_Basic_View(APIView):
    @swagger_auto_schema(
        operation_summary='发送评论',
        operation_description=
        '''
        发送格式{
            'activity_id':,
            'at_user_id':, // 被@ 用户
            'comment':
        }
        具体可查看补充接口 评论
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={201: 'OK', 400: '评论错误'}
    )
    def post(self, resquest):
        user_id = resquest.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data = resquest.data
        data['user_id'] = resquest.user.id
        # import pdb; pdb.set_trace()
        if 'at_user_id' not in data:
            data['at_user_id'] = 1
        else:
            try:
                user = User.objects.get(id=data['at_user_id'])
                activity = Activity.objects.get(id=data['activity_id'])
            except User.DoesNotExit or Activity.DoesNotExit:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            Notification(
                user=user,
                not_type=Notification.NotificationType.评论回复,
                type=Notification.Type.活动,
                activity=activity,
                content='您在{}活动下的评论收到回复'.format(activity.name),
                isread=False
            ).save()

        if len(data['comment']) == 0:
            return Response('评论不能为空', status=status.HTTP_400_BAD_REQUEST)

        data['comment_time'] = datetime.now()
        comment = Comment(**data)
        comment.save()
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Comment_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据评论id得到单个评论',
        responses={200: comment_response}
    )
    def get(self, resquest, id):
        comment = Comment.objects.get(id=id)
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='删除评论',
        responses={204: 'OK'}
    )
    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            comment = Comment.objects.get(id=id)
            if (not request.user.is_staff) and (comment.user != request.user):
                return Response(status=status.HTTP_403_FORBIDDEN)
            if request.user.is_staff:
                Notification(user=comment.user, not_type=Notification.NotificationType.系统通知, type=Notification.Type.活动, activity=comment.activity,
                             content="我们抱歉的通知您，您在活动 " + comment.activity.name + " 下的评论已经被管理员删除。").save()
                send_comment_deleted(user=comment.user, activity=comment.activity)
            comment.delete()
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Comment_Act_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据活动id 得到活动下所有评论',
        responses={201: comment_response}
    )
    def get(self, resquest, act_id):
        comment = Comment.objects.filter(activity_id=act_id)
        serializer = Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Comment_User_View(APIView):
    @swagger_auto_schema(
        operation_summary='得到用户所有评论',
        responses={201: comment_response}
    )
    def get(self, resquest):
        # user_id = resquest.user.id
        user_id = 1
        comment = Comment.objects.filter(user_id=user_id)
        serializer = Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
