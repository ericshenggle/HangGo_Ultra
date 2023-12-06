from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import *
from ars.models import *
from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework.response import Response
# from ars import activity, activity_tag, activity_type
import jieba
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.activity_type.serializers.type_get_serializers import Activity_Type_Get_Serializer
from ars.activity_tag.serializers.tag_get_serializers import Tag_Get_Serializer
from ars.search.serializers import Keyword_Serializer
from datetime import *
from ars.utils import change_data_time_format
from functools import cmp_to_key

keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY, description='关键字',
                            type=openapi.TYPE_STRING)
trend_response = openapi.Response('热搜', Keyword_Serializer)


class Search(APIView):
    @swagger_auto_schema(
        operation_summary='搜索',
        operation_description='按名字的关键字进行查询，可得到活动、类别、标签，内容与其对应GET方法请求的一致',
        manual_parameters=[keyword]
    )
    def get(self, request):
        user_id = request.user.id
        if user_id is None:
            user_id = 1
        user = User.objects.get(id=user_id)
        default_user = User.objects.get(id=1)
        params = request.query_params
        text = params['keyword']
        words = jieba.lcut(text)
        self.words = words
        if text not in words:
            words.append(text)
        activity_dict = {}
        type_dict = {}
        tag_dict = {}
        for w in words:
            activities = Activity.objects.filter(
                audit_status=Activity.AuditStatusChoice.审核通过,
            ).filter(name__contains=w)
            # if len(activities) > 0:
            if True:
                if w.strip() == '':
                    continue
                if w == text:
                    Keyword.objects.create(keyword=w, user=user)
                else:
                    Keyword.objects.create(keyword=w, user=default_user)
            for i in activities:
                if i.id not in activity_dict:
                    serializer = Activity_Get_Serializer(instance=i)
                    activity_dict[i.id] = serializer.data

            # activity_types = ActivityType.objects.filter(name__contains=w)    
            # for i in activity_types:
            #     if i.id not in type_dict:
            #         serializer = Activity_Type_Get_Serializer(instance=i) 
            #         type_dict[i.id] = serializer.data   

            # tags = Tag.objects.filter(name__contains=w)
            # for i in tags:
            #     if i.id not in tag_dict:
            #         serializer = Tag_Get_Serializer(instance=i) 
            #         tag_dict[i.id] = serializer.data  

        res = []
        for k, v in zip(activity_dict.keys(), activity_dict.values()):
            res.append({'type': 'activity', 'id': k, 'content': v})
        # for k, v in zip(type_dict.keys(), type_dict.values()):
        #     res.append({'type':'type', 'id':k, 'content':v})            
        # for k, v in zip(tag_dict.keys(), tag_dict.values()):
        #     res.append({'type':'tag', 'id':k, 'content':v})
        res.sort(key=cmp_to_key(self.cmp))
        return Response(res)

    def cmp(self, x, y):
        if self.calc_sim(x) < self.calc_sim(y):
            return 1
        else:
            return -1

    def calc_sim(self, x):
        sim = 0
        name = x['content']['name']
        for i in self.words:
            if i in name:
                sim += 1
        return sim

    @swagger_auto_schema(
        operation_summary='删除搜索历史',
        operation_description=
        '''
        发送格式{
            'id':[],
            'name':[],
        }
        ''',
        responses={204: 'OK', 404: '用户不存在'}
    )
    def post(self, request):
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
                    k = Keyword.objects.get(id=id)
                except Keyword.DoesNotExist:
                    continue
                if k.user_id != user_id:
                    continue
                k.delete()
        if 'name' in data:
            for name in data['name']:
                ks = Keyword.objects.filter(keyword=name)
                for k in ks:
                    if k.user_id != user_id:
                        continue
                    k.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class Search_Trend(APIView):
    @swagger_auto_schema(
        operation_summary='根据时间段搜索热搜词条',
        operation_description=
        """
        传入{
            'start':2021/1/1 1:11, //可以不传 默认为之前100天
            'end'2022/1/1 1:00: // 均为时间 可以不传 默认为现在
        }
        
        """,
        responses={200: trend_response}
    )
    def post(self, request):
        data = request.data
        now = datetime.now()
        td = timedelta(days=30)
        if 'start' in data:
            start = change_data_time_format(data['start'])
        else:
            start = now - td
        if 'end' in data:
            end = change_data_time_format(data['end'])
        else:
            end = now + td
        s = Keyword.objects.filter(search_time__range=(start, end)) \
                .values('keyword').annotate(search_tt=Count('keyword')).order_by('-search_tt')[:15]

        serializer = Keyword_Serializer(s, many=True)
        res = []
        for key in serializer.data:
            if key['keyword'] != '':
                res.append(key)
        return Response(res)


class Search_His(APIView):
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
        responses={200: trend_response, 404: '用户不存在'}
    )
    def post(self, request):
        if request.user.id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = request.data
        now = datetime.now()
        td = timedelta(days=100)
        if 'start' in data:
            start = change_data_time_format(data['start'])
        else:
            start = now - td
        if 'end' in data:
            end = change_data_time_format(data['end'])
        else:
            end = now
        s_list = Keyword.objects.filter(user_id=user_id).filter(search_time__range=(start, end)) \
            .order_by('-search_time')
        search_key = {}
        for s in s_list:
            if s.keyword not in search_key:
                search_key[s.keyword] = s
            elif search_key[s.keyword].search_time < s.search_time:
                search_key[s.keyword] = s

        search_list = list(search_key.values())
        search_list.sort(key=cmp_to_key(self.cmp))

        serializer = Keyword_Serializer(search_list, many=True)
        return Response(serializer.data)

    def cmp(self, x, y):
        if x.search_time < y.search_time:
            return -1
        else:
            return 1
