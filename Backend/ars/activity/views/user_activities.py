from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.activity.serializers.activity_info_serializer import ActivityInfo_Serializer
from ars.activity.serializers.activity_serializers import *
from ars.activity.serializers.activity_change_serializers import *
from ars.activity.serializers.activity_get_serializer import *
# from ars.activity.serializers.lecture_serializer import Lecture_Serializer
from ars.activity_type.serializers import *
from ars.models import *

from ars.utils import change_data_time_format
from datetime import *


class User_Create_Activities(APIView):

    @swagger_auto_schema(
        operation_summary='用户活动',
        operation_description=
        '''
        得到活动格式详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK', 400: '用户不存在'}
    )
    def get(self, request, id):
        user_id = id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = user.create_activities.filter(audit_status=Activity.AuditStatusChoice.审核通过)

        serializer = Activity_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class User_Create_Activities_Self(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='用户活动',
        operation_description=
        '''
        得到活动格式详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK', 400: '用户不存在'}
    )
    def get(self, request, id):
        user_id = id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = user.create_activities.exclude(audit_status=Activity.AuditStatusChoice.审核失败)

        serializer = Activity_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
