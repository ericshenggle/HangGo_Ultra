from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from ars.models import *
from ars.appealOrInform.serializers import *


class Appeal_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取全部申诉信息',
        responses={200: 'OK'}
    )
    def get(self, request):
        appeal_list = Appeal.objects.filter(isSave=False)
        serializer = Appeal_Serializer(instance=appeal_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='申诉',
        responses={201: 'OK'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesnotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if type(data['authority']) != int:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        appeal = Appeal(user=user, authority=data['authority'], reason=data['reason'])
        appeal.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='管理员将处理您的申诉',
            isread=False
        ).save()
        return Response(status=status.HTTP_201_CREATED)


class Inform_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取全部举报信息',
        responses={200: 'OK', 400: '错误'}
    )
    def get(self, request):
        inform_list = Inform.objects.filter(isSave=False)
        serializer = Inform_Serializer(instance=inform_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='举报',
        responses={201: 'OK', 400: '错误'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesnotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if type(data['authority']) != int:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if type(data['to_user_id']) != int:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            to_user = User.objects.get(id=data['to_user_id'])
        except User.DoesnotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        inform = Inform(user=user, to_user=to_user, authority=data['authority'], reason=data['reason'])
        inform.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='管理员将处理您对{}的举报'.format(inform.to_user.nickName),
            isread=False
        ).save()
        return Response(status=status.HTTP_201_CREATED)


class Appeal_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据id获取申诉信息',
        responses={200: 'OK'}
    )
    def get(self, request, id):
        try:
            appeal = Appeal.objects.get(id=id)
        except Appeal.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = Appeal_Serializer(instance=appeal)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Inform_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据id获取举报信息',
        responses={200: 'OK', 400: '错误'}
    )
    def get(self, request, id):
        try:
            inform = Inform.objects.get(id=id)
        except Inform.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = Inform_Serializer(instance=inform)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Appeal_Save_View(APIView):
    @swagger_auto_schema(
        operation_summary='驳回申诉',
        responses={200: 'OK'}
    )
    def delete(self, request):
        try:
            appeal = Appeal.objects.get(id=request.data['id'])
        except Appeal.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        appeal.isSave = True
        appeal.save()
        Notification(
            user=appeal.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='您的申诉已经被驳回，理由为：{}'.format(request.data['reason']),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='通过申诉',
        responses={201: 'OK'}
    )
    def post(self, request):
        try:
            appeal = Appeal.objects.get(id=request.data['id'])
        except Appeal.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        appeal.isSave = True
        user = appeal.user
        authority = list(user.authority)
        authority[appeal.authority] = '1'
        user.authority = ''.join(authority)
        user.save()
        appeal.save()
        Notification(
            user=appeal.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='您的申诉已经被通过，请查看您当前的权限',
            isread=False
        ).save()
        return Response(status=status.HTTP_201_CREATED)


class Inform_Save_View(APIView):
    @swagger_auto_schema(
        operation_summary='驳回举报',
        responses={200: 'OK', 400: '错误'}
    )
    def delete(self, request):
        try:
            inform = Inform.objects.get(id=request.data['id'])
        except Inform.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        inform.isSave = True
        inform.save()
        Notification(
            user=inform.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='您对{}的举报已经被驳回，理由为：{}'.format(inform.to_user.nickName, request.data['reason']),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='通过举报',
        responses={201: 'OK', 400: '错误'}
    )
    def post(self, request):
        try:
            inform = Inform.objects.get(id=request.data['id'])
        except Inform.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        inform.isSave = True
        user = inform.to_user
        authority = list(user.authority)
        authority[inform.authority] = '0'
        user.authority = ''.join(authority)
        user.save()
        inform.save()
        Notification(
            user=inform.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='您对{}的举报已经被通过'.format(inform.to_user.nickName),
            isread=False
        ).save()
        Notification(
            user=inform.to_user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.权限,
            content='您已被{}举报成功，理由为：{}'.format(inform.user.nickName, inform.reason),
            isread=False
        ).save()
        return Response(status=status.HTTP_201_CREATED)