from django.core.mail import send_mail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ars.models import *
from ars.notification.wxapi import send_user_audit_success, send_user_audit_fail, send_activity_audit_pass, \
    send_activity_audit_reject, send_new_activity_can_select
from ars.user.serializers import UserSuperAdminSerializer
from ars.user.serializers import UserAuthoritySerializer

class AuditUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=False)
    serializer_class = UserSuperAdminSerializer

    permission_classes = [permissions.IsAdminUser]

    # get方法和Retrive方法已经自带

    # 批准用户的注册！
    @swagger_auto_schema(
        operation_summary='审核通过用户注册',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='用户ID')
            },
        ),
        responses={200: '成功', 400: '非法用户ID'}
    )
    @action(methods=['post'], detail=False)
    def permit_audit(self, request):
        data = request.data
        if 'id' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=data['id'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user.is_active:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "该用户已经被审核"})
        user.is_active = True
        user.audit_status = User.AuditStatus.已通过
        user.save()
        send_mail(subject='您的用户审核通过', message='您好，您的账号审核已经通过。感谢您对本平台的使用与支持。',
                  recipient_list=[user.email], fail_silently=False, from_email=None)
        send_user_audit_success(user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='审核拒绝用户注册',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='用户ID')
            },
        ),
        responses={200: '成功', 400: '非法用户ID'}
    )
    @action(methods=['post'], detail=False)
    def reject_audit(self, request):
        data = request.data
        if 'id' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=data['id'])
        except  User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        send_mail(subject='您的用户审核失败', message='您好，我们抱歉地通知您，您的新建账号请求被管理员审核失败，如果您有疑问，请联系管理员。感谢您对本平台的使用与支持。',
                  recipient_list=[user.email], fail_silently=False, from_email=None)
        send_user_audit_fail(user)
        try:
            user.delete()
        except Exception:
            return Response(data={'message': '后端错误！用户删除功能前期在后端无法充分测试，请直接联系后端'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='审核通过活动',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='活动ID')
            },
        ),
        responses={200: '成功', 400: '非法活动ID'}
    )
    @action(methods=['post'], detail=False)
    def permit_activity(self, request):
        data = request.data
        if 'id' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            activity = Activity.objects.get(pk=data['id'])
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if activity.audit_status != Activity.AuditStatusChoice.审核中:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "该活动已经被审核"})
        activity.audit_status = Activity.AuditStatusChoice.审核通过
        activity.save()
        notification = Notification()
        notification.user = activity.create_user
        notification.activity = activity
        notification.content = "您好，您的活动" + activity.name + ' 已经审核通过，感谢您对本平台的使用与支持。'
        notification.isread = False
        notification.type = Notification.Type.活动
        notification.not_type = Notification.NotificationType.系统通知
        notification.save()
        subscribe_users = activity.activity_type.subscribe_users.all()
        followers = activity.create_user.followees.all()
        send_activity_audit_pass(activity)
        send_new_activity_can_select(activity)
        for user in subscribe_users:
            Notification(user=user, not_type=Notification.NotificationType.订阅提醒, type=Notification.Type.活动, isread=False,
                         activity=activity,
                         content='您订阅的类别' + activity.activity_type.name + '有新的活动' + activity.name + '！请点击查看').save()
        for user in followers:
            Notification(user=user, not_type=Notification.NotificationType.订阅提醒, type=Notification.Type.活动, isread=False,
                         activity=activity,
                         content='您关注的用户' + activity.create_user.username + '有新的活动' + activity.name + '发布！请点击查看').save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='审核拒绝活动',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='活动ID'),
                "reason": openapi.Schema(type=openapi.TYPE_STRING, description='拒绝理由')
            },
        ),
        responses={200: '成功', 400: '非法活动ID'}
    )
    @action(methods=['post'], detail=False)
    def reject_activity(self, request):
        data = request.data
        reason = request.data.get('reason', '')
        if len(reason) > 400:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "拒绝理由超过上限"})
        if 'id' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            activity = Activity.objects.get(pk=data['id'])
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if activity.audit_status != Activity.AuditStatusChoice.审核中:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "该活动已经被审核"})
        if activity.audit_status != Activity.AuditStatusChoice.审核通过:
            activity.audit_status = Activity.AuditStatusChoice.审核失败
            activity.save()
            send_mail(subject='您的活动审核失败', message="您好，我们抱歉地通知您，您的活动" +
                                                  activity.name + ' 被管理员审核失败，拒绝的理由为：' + reason + ' 如果您有疑问，请联系管理员。感谢您对本平台的使用与支持。',
                      recipient_list=[activity.create_user.email], fail_silently=False, from_email=None)
            notification = Notification()
            notification.user = activity.create_user
            notification.activity = activity
            notification.content = "您好，我们抱歉地通知您，您的活动" + activity.name + ' 被管理员审核失败，拒绝的理由为：' + reason + ' 如果您有疑问，请联系管理员。感谢您对本平台的使用与支持。'
            notification.isread = False
            notification.type = Notification.Type.活动
            notification.not_type = Notification.NotificationType.系统通知
            notification.save()
            send_activity_audit_reject(activity)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'message': 'Activity已经通过审核，无法撤销'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='审核拒绝委托',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='委托ID'),
                "reason": openapi.Schema(type=openapi.TYPE_STRING, description='拒绝理由')
            },
        ),
        responses={200: '成功', 400: '非法委托ID'}
    )
    @action(methods=['post'], detail=False)
    def reject_commission(self, request):
        data = request.data
        reason = request.data.get('reason', '')
        if len(reason) > 400:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "拒绝理由超过上限"})
        if 'id' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            commission = Commission.objects.get(id=data['id'])
        except Commission.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if commission.audit == Commission.AuditStatusChoice.审核失败:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "该委托已经被审核失败"})
        else:
            commission.audit = Commission.AuditStatusChoice.审核失败
            if commission.status == Commission.PublicStatusChoice.已申请:
                apply = Commission_Accept.objects.get(commission=commission)
                apply_user = apply.user
                apply.delete()
                commission.status = Commission.PublicStatusChoice.已发布
                notification = Notification()
                notification.user = apply_user
                notification.commission = commission
                notification.content = "您好，我们抱歉地通知您，您的委托" + commission.name + ' 被管理员审核失败，已自动取消你的申请，若想继续申请该委托请与发布者联系'
                notification.isread = False
                notification.type = Notification.Type.委托
                notification.not_type = Notification.NotificationType.系统通知
                notification.save()
            elif commission.status == Commission.PublicStatusChoice.已完成:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "该委托已经完成，无法撤销"})
            commission.save()
            send_mail(subject='您的委托审核失败', message="您好，我们抱歉地通知您，您的委托" +
                                                  commission.name + ' 被管理员审核失败，拒绝的理由为：' + reason + ' 如果您有疑问，请联系管理员。感谢您对本平台的使用与支持。',
                      recipient_list=[commission.user.email], fail_silently=False, from_email=None)
            notification = Notification()
            notification.user = commission.user
            notification.commission = commission
            notification.content = "您好，我们抱歉地通知您，您的委托" + commission.name + ' 被管理员审核失败，拒绝的理由为：' + reason + ' 如果您有疑问，请联系管理员。感谢您对本平台的使用与支持。'
            notification.isread = False
            notification.type = Notification.Type.委托
            notification.not_type = Notification.NotificationType.系统通知
            notification.save()
            # send_activity_audit_reject(commission)
            return Response(status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='修改用户权限',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='用户ID'),
                "authority": openapi.Schema(type=openapi.TYPE_STRING, description='权限字符串')
            },
        ),
        responses={201: '成功', 401: '非授权用户'}
    )
    @action(methods=['post'], detail=False)
    def change_authority(self, request):
        user_id = request.user.id
        if user_id is None or user_id != 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data_dict = request.data

        user = User.objects.get(id=data_dict['id'])
        user.authority = data_dict['authority']
        user.save()
        return Response(status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary='获取所有用户权限',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={200: '成功', 401: '非授权用户'}
    )
    @action(methods=['post'], detail=False)
    def user_all_authority(self, request):
        user_id = request.user.id
        if user_id is None or user_id != 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.all()
        serializer = UserAuthoritySerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='获取单个用户权限',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description='用户ID'),
            },
        ),
        responses={200: '成功', 401: '非授权用户'}
    )
    @action(methods=['post'], detail=False)
    def user_authority(self, request):
        user_id = request.user.id
        data = request.data
        if user_id is None or user_id != 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(id = data['id'])
        serializer = UserAuthoritySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='获取自身用户权限',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={200: '成功', 400: '非法用户'}
    )
    @action(methods=['post'], detail=False)
    def user_authority_self(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id = user_id)
        serializer = UserAuthoritySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)