from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.commission.serializers.comment_serializers import Commission_Comment_Serializer
from ars.models import *


class Commission_Score_View(APIView):
    @swagger_auto_schema(
        operation_summary='委托评分',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "commission_id": openapi.Schema(type=openapi.TYPE_INTEGER, description='commission_id'),
                "score": openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='评分（1-10之间的整数）')
            },
        ),
        responses={201: 'OK', 400: '评分不合法', 404: '委托不存在或者用户没有发布委托'}
    )
    def post(self, request):
        commission_id = request.data.pop('commission_id', None)
        score = int(request.data.pop('score', 1))
        if commission_id is None:
            return Response('委托不存在', status=status.HTTP_400_BAD_REQUEST)
        try:
            commission = Commission.objects.get(id=commission_id)
        except Commission.DoesNotExist:
            return Response('委托不存在', status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user_id != commission.user.id:
            return Response('非本委托创建人不能评价本委托', status=status.HTTP_400_BAD_REQUEST)
        try:
            apply = Commission_Accept.objects.filter(commission_id=commission_id).first()
        except Commission_Accept.DoesNotExist:
            return Response('本委托未有人申请，不能进行评价', status=status.HTTP_400_BAD_REQUEST)
        if commission.status != Commission.PublicStatusChoice.已完成:
            return Response('本委托申请人仍未完成委托，不能进行评价', status=status.HTTP_400_BAD_REQUEST)
        try:
            userCommission = UserCommission.objects.get(user_id=apply.user_id, commission_id=commission_id)
        except UserCommission.DoesNotExist:
            if score > 10 or score < 1:
                return Response('分数错误', status=status.HTTP_400_BAD_REQUEST)
            userCommission = UserCommission(user_id=apply.user_id, commission_id=commission_id, score=score)
            userCommission.save()
            commission.status = Commission.PublicStatusChoice.已评分
            commission.save()
            Notification(
                user_id=apply.user_id,
                not_type=Notification.NotificationType.委托评分,
                type=Notification.Type.委托,
                commission_id=commission_id,
                content='您在{}委托完成之后收到评分'.format(commission.name),
                isread=False
            ).save()
            # TODO
            return Response(status=status.HTTP_201_CREATED)
        return Response('本委托已完成评价', status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='删除评分',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "commission_id": openapi.Schema(type=openapi.TYPE_INTEGER, description='commission_id'),
            },
        ),
        responses={204: 'OK'}
    )
    def delete(self, request):
        commission_id = request.data.pop('commission_id', None)
        if commission_id is None:
            return Response('委托不存在', status=status.HTTP_400_BAD_REQUEST)
        try:
            commission = Commission.objects.get(id=commission_id)
        except Commission.DoesNotExist:
            return Response('委托不存在', status=status.HTTP_400_BAD_REQUEST)
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user_id != commission.user.id:
            return Response('非本委托创建人不能取消本委托的评价', status=status.HTTP_400_BAD_REQUEST)
        userCommission = UserCommission.objects.get(commission_id=commission_id)
        apply_user_id = UserCommission.user.id
        userCommission.delete()
        Notification(
            user_id=apply_user_id,
            not_type=Notification.NotificationType.委托评分,
            type=Notification.Type.委托,
            commission_id=commission_id,
            content='您在{}委托完成之后的评分已被删除'.format(commission.name),
            isread=False
        ).save()
        # TODO
        return Response(status=status.HTTP_204_NO_CONTENT)


class Commission_Comment_View(APIView):
    @swagger_auto_schema(
        operation_summary='委托评论',
        operation_description=
        '''
        发送格式{
            'commission_id':,
            'to_user_id':, // 被@ 用户
            'comment':,
            'to_comment_id':,  //一级评论id
        }
        ''',
        responses={201: 'OK', 400: '评论错误'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        try:
            user = User.objects.get(id=user_id)
            commission = Commission.objects.get(id=data['commission_id'])
        except User.DoesNotExit or Commission.DoesNotExit:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        if len(data['comment']) == 0:
            return Response('评论不能为空', status=status.HTTP_400_BAD_REQUEST)
        authority = user.authority
        if authority[1] == '0':
            return Response('当前用户无发布评论权限，请及时进行申诉', status=status.HTTP_400_BAD_REQUEST)
        to_user_id = data.pop('to_user_id', None)
        to_comment_id = data.pop('to_comment_id', None)
        if to_comment_id is None:
            comment = Commission_Comment(user_id=user.id, commission_id=commission.id, comment=data['comment'])
            comment.save()
            Notification(
                user=commission.user,
                not_type=Notification.NotificationType.评论回复,
                type=Notification.Type.委托,
                commission=commission,
                content='您在{}委托下收到评论回复'.format(commission.name),
                isread=False
            ).save()
            # TODO
        else:
            try:
                to_comment = Commission_Comment.objects.get(id=to_comment_id)
            except Commission_Comment.DoesNotExist:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            if to_user_id is not None:
                try:
                    to_user = User.objects.get(id=to_user_id)
                except User.DoesNotExist:
                    return Response({}, status=status.HTTP_404_NOT_FOUND)
                comment = Commission_Comment_Reply(user_id=user.id, comment=data['comment'], to_user_id=to_user.id, to_comment_id=to_comment.id)
                comment.save()
                Notification(
                    user=to_user,
                    not_type=Notification.NotificationType.评论回复,
                    type=Notification.Type.委托,
                    commission=commission,
                    content='您在{}委托下评论{}的评论收到回复'.format(commission.name, to_user.nickName),
                    isread=False
               ).save()
               # TODO
            else:
                comment = Commission_Comment_Reply(user_id=user.id, comment=data['comment'], to_comment_id=to_comment.id)
                comment.save()
                Notification(
                    user=to_comment.user,
                    not_type=Notification.NotificationType.评论回复,
                    type=Notification.Type.委托,
                    commission=commission,
                    content='您在{}委托下的评论收到回复'.format(commission.name),
                    isread=False
               ).save()
               # TODO
        return Response(status=status.HTTP_201_CREATED)


comment_response = openapi.Response('comment', Commission_Comment_Serializer)


class Commission_Comment_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据评论id得到单个评论',
        responses={200: comment_response}
    )
    def get(self, resquest, id):
        comment = Commission_Comment.objects.get(id=id)
        serializer = Commission_Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='删除评论',
        responses={204: 'OK'}
    )
    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            comment = Commission_Comment.objects.get(id=id)
            if (not request.user.is_staff) and (comment.user != request.user):
                return Response(status=status.HTTP_403_FORBIDDEN)
            if request.user.is_staff:
                Notification(user=comment.user,
                            not_type=Notification.NotificationType.系统通知, 
                            type=Notification.Type.委托, 
                            commission=comment.commission,
                            content="我们抱歉的通知您，您在委托 " + comment.commission.name + " 下的评论已经被管理员删除。").save()
                # send_comment_deleted(user=comment.user, activity=comment.activity)
            comment.delete()
        except Commission_Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Commission_Comment_Com_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据委托id得到委托下所有评论',
        responses={201: comment_response}
    )
    def get(self, resquest, com_id):
        comment = Commission_Comment.objects.filter(commission_id=com_id)
        serializer = Commission_Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Commission_Comment_User_View(APIView):
    @swagger_auto_schema(
        operation_summary='得到用户所有评论',
        responses={201: comment_response}
    )
    def get(self, resquest):
        user_id = resquest.user.id
        comment = Commission_Comment.objects.filter(user_id=user_id)
        serializer = Commission_Comment_Serializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)