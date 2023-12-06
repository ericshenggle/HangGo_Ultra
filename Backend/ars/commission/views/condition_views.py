from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from ars.activity.serializers.activity_change_serializers import *
from ars.commission.serializers.commission_get_serializers import Commission_Get_Serializer
from ars.models import *
from ars.utils import change_data_time_format


class condition_Top_View(APIView):
    @swagger_auto_schema(
        operation_summary='委托筛选',
        operation_description=
        '''
        可以包括以下任意值
        {
            'user_id': int,  //创建者
            'user_accept': int,  //接收者
            'commission_type':{
                'methods': str,          //id or name
                'values':[]
            },
            'location': int,
            'status': int,
            'audit': int,
            'start_time_timerange': {
                'start': str,
                'end': str
            }
            ...
        }
        ''',
        responses={200: 'OK', 400: '用户不存在'}
    )
    def post(self, request):
        param = request.data
        queryset = Commission.objects.all()
        user_id = None
        if 'user_id' in param and type(param['user_id']) == int:
            user_id = param['user_id']
            user = User.objects.get(id=user_id)
            queryset = user.create_commissions.all()
        elif 'user_accept' in param and type(param['user_accept']) == int:
            user_id = param['user_accept']
            user = User.objects.get(id=user_id)
            queryset = user.accept_commissions.all()

        if 'location' in param:
            queryset = queryset.filter(location__in=param['location'])

        if 'status' in param:
            queryset = queryset.filter(status__in=param['status'])

        if 'audit' in param:
            queryset = queryset.filter(audit__in=param['audit'])

        if 'commission_type' in param:
            if param['types']['method'] == 'id':
                queryset = queryset.filter(Commission_type__id__in=param['types']['value'])
            elif param['types']['method'] == 'name':
                queryset = queryset.filter(Commission_type__name__in=param['types']['value'])

        if 'start_time_timerange' in param:
            pa = param["start_time_timerange"]
            try:
                start = change_data_time_format(pa['start'])
                end = change_data_time_format(pa['end'])
            except ValueError or KeyError:
                return Response('时间错误', status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(start_time__range=(start, end)).order_by('start_time')

        serializer = Commission_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
