from datetime import *
from functools import cmp_to_key

import jieba
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.commission.serializers.commission_get_detail_serializers import *
from ars.commission.serializers.commission_get_serializers import *
from ars.commission.serializers.commission_history_serializers import Commission_SearchRecord_Serializer

from ars.models import *
from ars.utils import change_data_time_format


class Commission_All_Admin_View(APIView):

    @swagger_auto_schema(
        operation_summary='管理端获取所有审核通过的委托',
        responses={200: 'OK'}
    )
    def get(self, request):
        commission_list = Commission.objects.exclude(audit=Commission.AuditStatusChoice.审核失败).exclude(
                    status=Commission.PublicStatusChoice.已完成).order_by('-create_time')
        serializer = Commission_Get_Serializer(instance=commission_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class Commission_All_View(APIView):

    @swagger_auto_schema(
        operation_summary='小程序获取当前有效的委托',
        responses={200: 'OK'}
    )
    def get(self, request):
        td = timedelta(days=100)
        now = datetime.now()
        commission_list = Commission.objects.exclude(audit=Commission.AuditStatusChoice.审核失败).filter(
                    status=Commission.PublicStatusChoice.已发布, end_time__range=(now, now + td)).order_by('-create_time')
        serializer = Commission_Get_Serializer(instance=commission_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='根据info获取所有审核通过的委托',
        operation_description=
        '''
            {
                "info": str
            }
        ''',
        responses={200: 'OK'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            user_id = 1
        user = User.objects.get(id=user_id)
        default_user = User.objects.get(id=1)
        params = request.data.copy()
        text = params['info']
        if text is None or text == '':
            return Response('空输入',status=status.HTTP_400_BAD_REQUEST)
        words = jieba.lcut(text)
        self.words = words
        if text not in words:
            words.append(text)
        commission_dict = {}
        td = timedelta(days=100)
        now = datetime.now()
        for w in words:
            commissions = Commission.objects.filter(
                audit=Commission.AuditStatusChoice.审核通过, status=Commission.PublicStatusChoice.已发布, end_time__range=(now, now + td)
            ).filter(name__contains=w).order_by('-create_time')
            if w.strip() == '':
                continue
            if w == text:
                SearchRecord_Commission.objects.create(keyword=w, user=user)
            else:
                SearchRecord_Commission.objects.create(keyword=w, user=default_user)
            for i in commissions:
                if i.id not in commission_dict:
                    serializer = Commission_Get_Serializer(instance=i)
                    commission_dict[i.id] = serializer.data

        res = []
        for k, v in zip(commission_dict.keys(), commission_dict.values()):
            res.append(v)
        res.sort(key=cmp_to_key(self.cmp))
        return Response(res)

    def cmp(self, x, y):
        if self.calc_sim(x) < self.calc_sim(y):
            return 1
        else:
            return -1

    def calc_sim(self, x):
        sim = 0
        name = x['name']
        for i in self.words:
            if i in name:
                sim += 1
        return sim


class Commission_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取单个委托详情',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={200: 'OK', 204: '没有传入键值', 404: '没有该活动'}
    )
    def post(self, request):
        commission_id = request.data.pop('commission_id', None)
        if commission_id is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            commission = Commission.objects.get(id=commission_id)
        except Commission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_id = request.user.id
        if user_id is None:
            user_id = 1
        serializer = Commission_Get_Detail_Serializer(instance=commission)

        click = ClickRecord_Commission(
            commission_id=commission_id, user_id=user_id
        )
        click.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class Commission_History_View(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='根据时间段搜索用户历史搜索词条',
        operation_description=
        """
        输入{
            'start':2021/1/1 1:11, //可以不传 默认为之前100天
            'end'2022/1/1 1:00: // 均为时间 可以不传 默认为现在
        }
        """,   
        responses={200: '成功', 404: '用户不存在'}
    )
    def post(self, request):
        if request.user.id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        now = datetime.now()
        data = request.data
        td = timedelta(days=100)
        if 'start' in data:
            start = change_data_time_format(data['start'])
        else:
            start = now - td
        if 'end' in data:
            end = change_data_time_format(data['end'])
        else:
            end = now
        s_list = SearchRecord_Commission.objects.filter(user_id=user_id).filter(search_time__range=(start, end)) \
            .order_by('-search_time')
        search_key = {}
        for s in s_list:
            if s.keyword not in search_key:
                search_key[s.keyword] = s
            elif search_key[s.keyword].search_time < s.search_time:
                search_key[s.keyword] = s

        search_list = list(search_key.values())
        search_list.sort(key=cmp_to_key(self.cmp))

        serializer = Commission_SearchRecord_Serializer(search_list, many=True)
        return Response(serializer.data)

    def cmp(self, x, y):
        if x.search_time < y.search_time:
            return -1
        else:
            return 1

    @swagger_auto_schema(
        operation_summary='删除搜索历史',
        operation_description=
        '''
        发送格式{
            'id':[],
            'keyword':[],
        }
        ''',
        responses={204: 'OK', 404: '用户不存在'}
    )
    def delete(self, request):
        if request.user.id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if 'id' in data:
            for id in data['id']:
                try:
                    k = SearchRecord_Commission.objects.get(id=id)
                except SearchRecord_Commission.DoesNotExist:
                    return Response(status=status.HTTP_400_NOT_FOUND)
                if k.user_id != user_id:
                    return Response('不能删除他人用户的历史信息',status=status.HTTP_404_NOT_FOUND)
                k.delete()
        if 'keyword' in data:
            for name in data['keyword']:
                ks = SearchRecord_Commission.objects.filter(keyword=name)
                for k in ks:
                    if k.user_id != user_id:
                        continue
                    k.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)