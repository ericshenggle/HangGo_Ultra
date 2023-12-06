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

from ars.utils import change_data_time_format
from datetime import *

class condition_Act_View(APIView):
    @swagger_auto_schema(
        operation_summary='活动筛选',
        operation_description=
        '''
        得到活动格式详细请看补充文档 活动筛选 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200:'OK', 400:'用户不存在'}
    )
    def post(self, request):
        param = request.data
        queryset = Activity.objects.all()
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

        if 'normal_activity' in param and param['normal_activity'] == True:
            queryset = queryset.exclude(type__name__contains='课')

        if 'id' in param:
            queryset = queryset.filter(id__in=param['id'])
        if 'name' in param:
            queryset = queryset.filter(name__in=param['name'])

        if 'location' in param:
            queryset = queryset.filter(location__in=param['location'])

        if 'public_status' in param:
            queryset = queryset.filter(public_status__in=param['public_status'])

        if 'audit_status' in param:
            queryset = queryset.filter(audit_status__in=param['audit_status'])

        if 'start_enroll_timerange' in param:
            pa = param["start_enroll_timerange"]
            try:
                start = change_data_time_format(pa['start'])
                end = change_data_time_format(pa['end'])
            except ValueError or KeyError:
                return Response('时间错误',status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(start_enrollment_at__range=(start,end)).order_by('start_enrollment_at')

        if 'timerange' in param:
            pa = param["timerange"]
            try:
                start = change_data_time_format(pa['start'])
                end = change_data_time_format(pa['end'])
            except ValueError or KeyError:
                return Response('时间错误',status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(normal_activity__start_at__range=(start,end)).order_by('normal_activity__start_at')

        if 'types' in param:
            if param['types']['method'] == 'id':
                queryset = queryset.filter(activity_type__id__in=param['types']['value'])
            elif param['types']['method'] == 'name':
                queryset = queryset.filter(activity_type__name__in=param['types']['value'])

        if 'tags' in param:
            if param['tags']['method'] == 'id':
                queryset = queryset.filter(tags__id__in=param['tags']['value'])           
            elif param['tags']['method'] == 'name':
                queryset = queryset.filter(tags__name__in=param['tags']['value']) 
        

        if 'activity_status' in param:
            now_time = datetime.now()
            if param['activity_status'] == 1: # 未开始
                queryset = queryset.filter(normal_activity__start_at__gt=now_time)
            elif param['activity_status'] == 2: # 进行中
                queryset = queryset.filter(
                    normal_activity__start_at__lte=now_time
                ).filter(normal_activity__end_at__gte=now_time)
            elif param['activity_status'] == 3: # 已结束
                queryset = queryset.filter(normal_activity__end_at__lt=now_time)
            elif param['activity_status'] == 4: # 未结束
                queryset = queryset.filter(normal_activity__end_at__gt=now_time)


        if 'order_by_id' in param:
            queryset = queryset.order_by('id')
        else:
            queryset = queryset.order_by('-id')
        serializer = Activity_Get_Serializer(instance=queryset, many=True) 
        return Response(serializer.data,status=status.HTTP_200_OK)
        



