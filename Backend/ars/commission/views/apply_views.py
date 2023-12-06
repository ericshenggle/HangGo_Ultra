from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.commission.serializers.commission_apply_serializers import Apply_Get_Serializer
from ars.models import *
from datetime import *


class Commission_Apply_View(APIView):
    @swagger_auto_schema(
        operation_summary='申请委托',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={201: 'created', 400: '错误信息', 404: '用户不存在'}
    )
    def post(self, request):
        commission_id = request.data.pop('commission_id', None)
        if commission_id is None or commission_id == '':
            return Response('委托id没传入', status=status.HTTP_400_BAD_REQUEST)
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

        if user_id == commission.user.id:
            return Response('本委托创建人不能接受本委托', status=status.HTTP_400_BAD_REQUEST)
        apply = Commission_Accept.objects.filter(commission_id=commission_id).first()
        if apply:
            return Response('本委托已被接受', status=status.HTTP_400_BAD_REQUEST)
        if commission.end_time <= datetime.now():
            return Response('本委托时间已结束，无法申请', status=status.HTTP_400_BAD_REQUEST)
        authority = user.authority
        if authority[3] == '0':
            return Response('当前用户无申请委托权限，请及时进行申诉', status=status.HTTP_400_BAD_REQUEST)
        apply = Commission_Accept(user_id=user_id, commission_id=commission_id)
        apply.save()
        commission.status = Commission.PublicStatusChoice.已申请
        commission.user_accept = user
        commission.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您已接受来自{}的{}委托'.format(commission.user.nickName, commission.name),
            isread=False
        ).save()
        Notification(
            user=commission.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您的{}委托已被{}申请接受'.format(commission.name, user.nickName),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)


class Commission_Apply_Status_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据委托状态查看用户申请的委托',
        responses={200: 'OK', 400: '错误信息', 404: '用户不存在'}
    )
    def get(self, request, Status):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        Status = int(Status)
        commission_accept_list = user.commission_accept_set.filter(commission__status=Status).order_by('-apply_time')

        serializer = Apply_Get_Serializer(instance=commission_accept_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Commission_Drop_View(APIView):
    @swagger_auto_schema(
        operation_summary='放弃委托',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={200: 'OK', 400: '错误信息', 404: '用户不存在'}
    )
    def post(self, request):
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

        try:
            apply = Commission_Accept.objects.get(user_id=user_id, commission_id=commission_id)
        except Commission_Accept.DoesNotExist:
            return Response('用户未接受该委托', status=status.HTTP_400_BAD_REQUEST)

        apply.delete()
        commission.status = Commission.PublicStatusChoice.已发布
        commission.user_accept = None
        commission.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您已放弃来自{}的{}委托'.format(commission.user.nickName, commission.name),
            isread=False
        ).save()
        Notification(
            user=commission.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您的{}委托已被{}放弃'.format(commission.name, user.nickName),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)


class Commission_Terminate_View(APIView):
    @swagger_auto_schema(
        operation_summary='终止委托',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={200: 'OK', 400: '错误信息', 404: '用户不存在'}
    )
    def post(self, request):
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
            return Response('非本委托创建人不能终止本委托', status=status.HTTP_400_BAD_REQUEST)

        apply = Commission_Accept.objects.filter(commission_id=commission_id).first()
        if apply is None:
            return Response('本委托未有人申请', status=status.HTTP_400_BAD_REQUEST)
        Notification(
            user=apply.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您接受的来自{}的{}委托已被终止'.format(commission.user.nickName, commission.name),
            isread=False
        ).save()
        apply.delete()
        commission.status = Commission.PublicStatusChoice.已发布
        commission.user_accept = None
        commission.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您的{}委托已终止，恢复到未被申请状态'.format(commission.name),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)


class Commission_Finish_View(APIView):
    @swagger_auto_schema(
        operation_summary='完成委托',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={200: 'OK', 400: '错误信息', 404: '用户不存在'}
    )
    def post(self, request):
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
        apply = Commission_Accept.objects.filter(commission_id=commission_id).first()
        if apply is None:
            return Response('本委托未有人申请，不能完成', status=status.HTTP_400_BAD_REQUEST)
        if user_id != apply.user.id:
            return Response('非本委托申请人不能完成本委托', status=status.HTTP_400_BAD_REQUEST)

        commission.status = Commission.PublicStatusChoice.已完成
        commission.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您已完成来自{}的{}委托，等待创建者同意和打分'.format(commission.user.nickName, commission.name),
            isread=False
        ).save()
        Notification(
            user=commission.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您的{}委托已被{}完成，请及时同意并打分'.format(commission.name, user.nickName),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='撤销完成委托',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={200: 'OK', 400: '错误信息', 404: '用户不存在'}
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
        if commission.status != Commission.PublicStatusChoice.已完成:
            return Response('本委托申请人完成，不能撤销', status=status.HTTP_400_BAD_REQUEST)
        if user_id != commission.user.id:
            return Response('非本委托创建人不能进行撤销完成本委托操作', status=status.HTTP_400_BAD_REQUEST)

        commission.status = Commission.PublicStatusChoice.已申请
        commission.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您完成来自{}的{}委托已被撤销，请及时与发布者沟通'.format(commission.user.nickName, commission.name),
            isread=False
        ).save()
        Notification(
            user=commission.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您已撤销{}完成的{}委托，请及时与申请者沟通'.format(user.nickName, commission.name),
            isread=False
        ).save()
        return Response(status=status.HTTP_200_OK)
