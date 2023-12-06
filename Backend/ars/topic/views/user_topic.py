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
from ars.topic.serializers.topic_get_serializer import Topic_Get_Serializer

from ars.utils import change_data_time_format
from datetime import *


class User_Create_Topic(APIView):

    @swagger_auto_schema(
        operation_summary='用户话题',
        operation_description=
        '''
        得到话题格式详细请看补充文档 话题查看 接口
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
        queryset = user.create_topics.all().filter(audit=Topic.AuditStatusChoice.审核通过).order_by('-create_at')

        serializer = Topic_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class User_Create_Topic_Self(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='用户话题',
        operation_description=
        '''
        得到话题格式详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK', 400: '用户不存在'}
    )
    def get(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = user.create_topics.all().order_by('-create_at')

        serializer = Topic_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
