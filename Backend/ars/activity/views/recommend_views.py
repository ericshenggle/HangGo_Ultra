from django.contrib.auth.models import User, Group
from django.db.models import Count
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

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

from ars.activity.recommend.recommend import recommend_activity
from ars.utils import change_data_time_format
from datetime import *

class recommend_View(APIView):
    @swagger_auto_schema(
        operation_summary='活动推荐',
        responses={200:'OK'}
    )
    def post(self, request):
        data = request.data 
        if request.user.id is None:
            now = datetime.now()
            td = timedelta(days=30)
            request.data['start'] = now - td
            request.data['end'] = now + td 
            return trend_View().post(request)
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        click_record = ClickRecord.objects.filter(user_id=user.id)
        if len(click_record) == 0 and len(user.attend_activities.all()) == 0:
            now = datetime.now()
            td = timedelta(days=30)
            request.data['start'] = now - td
            request.data['end'] = now + td 
            return trend_View().post(request)            

        recommend_tmp_act_list = recommend_activity(user) 
        recommend_act_list = []
        for act in recommend_tmp_act_list:
            if act.audit_status == Activity.AuditStatusChoice.审核通过 \
                and act.activity_type_id != 9:
                recommend_act_list.append(act)
        serializer = Activity_Get_Serializer(instance=recommend_act_list, many=True)
        hot = trend_View().post(request, ret=False)
        return Response(serializer.data + hot) 

                
class trend_View(APIView):
    @swagger_auto_schema(
        operation_summary='热门活动',
        operation_description=
        """
        传入{
            'start':2021/1/1 1:11, // 可不传， 默认为前10天
            'end'2022/1/1 1:00: // 可不传，默认为当前，均为时间
        }
        """,   
        responses={200:'OK'}
    )
    def post(self, request, ret=True):
        now = datetime.now()
        td = timedelta(days=10)
        data = request.data
        if 'start' not in data:
            start = now - td
        elif type(data['start']) == str:
            start = change_data_time_format(data['start'])
        else:
            start = data['start']
        if 'end' not in data:
            end = now + td
        elif type(data['end']) == str: 
            end = change_Activity_format(data['end'])
        else:
            end = data['end']

        click_record = ClickRecord.objects.filter(click_time__range=(start, end))
        activities = click_record.values('activity_id')\
            .annotate(act_num = Count('activity')).order_by('-act_num')[:20]
        activity_list = []
        for i in activities:
            activity = Activity.objects.get(id=i['activity_id'])
            # now_ = now.replace(tzinfo=pytz.timezone('UTC'))
            if len(activity.normal_activity.all()) == 0:
                continue
            if activity.normal_activity.all()[0].end_at >= now \
                and activity.audit_status == Activity.AuditStatusChoice.审核通过 \
                and activity.activity_type_id != 9:
                activity_list.append(activity)
                # print(activity.name)
        serializer = Activity_Get_Serializer(
            instance=activity_list, 
            many=True,
            context = {'start':start, 'end':end}
        )
        if ret == False:
            return serializer.data
        return Response(serializer.data)
 