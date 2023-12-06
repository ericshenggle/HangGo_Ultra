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
from rest_framework.permissions import IsAuthenticated
from ars.models import *
from datetime import *
# Create your views here.

start_time = openapi.Parameter('start_time', in_=openapi.IN_QUERY, description='年/月/日 小时/分钟',
                                            type=openapi.FORMAT_DATETIME)
end_time = openapi.Parameter('end_time', in_=openapi.IN_QUERY, description='年/月/日 小时/分钟',
                                            type=openapi.FORMAT_DATETIME)

from ars.utils import change_data_time_format

class Activity_Schedule_View(APIView):

    @swagger_auto_schema(
        operation_summary='根据时间获取所有活动',
        operation_description=
        '''
        得到活动格式详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        manual_parameters=[start_time, end_time],
        responses={200:'OK'}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request):
        params = request.query_params
        start = change_data_time_format(params['start_time'])
        end = change_data_time_format(params['end_time'])

        activity_list = Activity.objects.filter(start_enrollment_at__range=(start,end))
        serializer = Activity_Get_Serializer(instance=activity_list, many=True) 

        return Response(serializer.data,status=status.HTTP_200_OK)

class Activity_User_Schedule_View(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary='用户根据时间获取所有活动',
        operation_description=
        '''
        得到活动格式详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        manual_parameters=[start_time, end_time],
        responses={200:'OK'}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request):
        # import pdb; pdb.set_trace()
        user_id = request.user.id
        if user_id is None:
            return Response([])
        # user_id = 12
        params = request.query_params
        start = change_data_time_format(params['start_time'])
        end = change_data_time_format(params['end_time'])
        user = User.objects.get(id=user_id)
        activity_list = user.attend_activities.filter(start_enrollment_at__range=(start,end)).order('start_at')
        serializer = Activity_Get_Serializer(instance=activity_list, many=True) 

        return Response(serializer.data,status=status.HTTP_200_OK)


