from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from ars.commission.serializers.commission_get_serializers import Commission_Get_Serializer
from ars.models import *

from ars.commission.recommend.recommend import recommend_commission
from ars.utils import change_data_time_format
from datetime import *


class recommend_View(APIView):
    @swagger_auto_schema(
        operation_summary='委托推荐',
        responses={200: 'OK'}
    )
    def post(self, request):
        data = request.data
        if request.user.id is None:
            now = datetime.now()
            td = timedelta(days=10)
            request.data['start'] = now
            request.data['end'] = now + td
            return trend_View().post(request)
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        click_record = ClickRecord_Commission.objects.filter(user_id=user.id)
        if len(click_record) == 0 and len(user.finish_commissions.all()) == 0:
            now = datetime.now()
            td = timedelta(days=10)
            request.data['start'] = now
            request.data['end'] = now + td
            return trend_View().post(request)

        recommend_tmp_com_list = recommend_commission(user)
        recommend_com_list = []
        for com in recommend_tmp_com_list:
            if com.audit == Commission.AuditStatusChoice.审核通过 and com.status == Commission.PublicStatusChoice.已发布:
                recommend_com_list.append(com)
        serializer = Commission_Get_Serializer(instance=recommend_com_list, many=True)
        hot = trend_View().post(request, ret=False)
        return Response(serializer.data + hot)


class trend_View(APIView):
    def post(self, request, ret=True):
        now = datetime.now()
        td = timedelta(days=10)
        data = request.data
        if 'start' not in data:
            start = now
        elif type(data['start']) == str:
            start = change_data_time_format(data['start'])
        else:
            start = data['start']
        if 'end' not in data:
            end = now + td
        elif type(data['end']) == str:
            end = change_data_time_format(data['end'])
        else:
            end = data['end']

        click_record = ClickRecord_Commission.objects.filter(click_time__range=(start, end))
        commissions = click_record.values('commission_id') \
                          .annotate(com_num=Count('commission')).order_by('-com_num')[:20]
        commission_list = []
        for i in commissions:
            commission = Commission.objects.get(id=i['commission_id'])
            if commission.start_time >= now \
                    and commission.audit == Commission.AuditStatusChoice.审核通过   \
                    and commission.status == Commission.PublicStatusChoice.已发布:
                commission_list.append(commission)
                # print(activity.name)
        serializer = Commission_Get_Serializer(
            instance=commission_list,
            many=True,
            context={'start': start, 'end': end}
        )
        if not ret:
            return serializer.data
        return Response(serializer.data)
