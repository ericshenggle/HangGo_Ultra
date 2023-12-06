from django.contrib.auth.models import User, Group
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView

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

class condition_Top_View(APIView):
    @swagger_auto_schema(
        operation_summary='话题筛选',
        operation_description=
        '''
        得到活动格式详细请看补充文档 话题筛选 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200:'OK', 400:'用户不存在'}
    )
    def post(self, request):
        param = request.data
        queryset = Topic.objects.all().filter(audit=Topic.AuditStatusChoice.审核通过,).order_by('-create_at')
        user_id = None
        if 'user_id' in param:
            user_id = param['user_id']

        if 'user_attend' in param and param['user_attend'] == True:
            if user_id is None:
                user_id = request.user.id
            if user_id is not None:
                user = User.objects.get(id=user_id)
                queryset = user.attend_activities.all()
        elif 'user_create' in param and param['user_create'] == True:
            if user_id is None:
                user_id = request.user.id
            if user_id is not None:
                user = User.objects.get(id=user_id)
                queryset = user.create_activities.all()

        if 'types' in param:
            if param['types']['method'] == 'id':
                queryset = queryset.filter(topic_type__id__in=param['types']['value'])
            elif param['types']['method'] == 'name':
                queryset = queryset.filter(topic_type__name__in=param['types']['value'])

        serializer = Topic_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
        



