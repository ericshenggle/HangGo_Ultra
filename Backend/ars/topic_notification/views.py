from django.contrib.auth.decorators import permission_required, login_required
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes

from ars.custom_permissions.custom_permissions import IsUser
from django.http import JsonResponse
from rest_framework.decorators import action

from ars.topic_notification.serializers import Topic_NotificationSerializer
from ars.utils import code2session
from ars.models import Notification, Topic_Notification
from django.shortcuts import get_object_or_404
from ars.notification.serializers import NotificationSerializer
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404


class Topic_NotificationViewSet(viewsets.ModelViewSet):
    queryset = Topic_Notification.objects.all()
    serializer_class = Topic_NotificationSerializer

    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary='获取当前用户的所有通知',
        operation_description='默认做了分页，下表中的那个page为页数参数'
    )
    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        queryset = request.user.notification_set.all().order_by('-id')
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='标记所有通知为已读',
        operation_description='下表中的pk直接为该通知的ID，该通知之前是否是已读的不做检查，无条件返回204 NO CONTENT',
        responses={204: ''}
    )
    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def read(self, request, pk=None):
        notifications = request.user.notification_set.all()
        for notification in notifications:
            notification.isread = True
            notification.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='标记某个通知为已读',
        operation_description='下表中的pk直接为该通知的ID，该通知之前是否是已读的不做检查，无条件返回204 NO CONTENT',
        responses={204: '标记成功'}
    )
    @action(methods=['get'], detail=True, permission_classes=[IsUser])
    def read_notification(self, request, pk=None):
        instance = self.get_object()
        instance.isread = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes=[IsUser])
    def user_delete(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def user_deleteall(self, request):
        request.user.notification_set.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
