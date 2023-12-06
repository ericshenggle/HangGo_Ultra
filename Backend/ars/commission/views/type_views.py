from functools import cmp_to_key

import jieba
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.commission.serializers.type_get_serializers import *
from ars.commission.serializers.type_serializers import Commission_Type_Serializer

from ars.models import *
import base64

type_simple_get_response = openapi.Response('response description', Commission_Type_Simple_Get_Serializer)

class Commission_Sort_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据类别获取所有审核通过的委托',
        responses={200: 'OK'}
    )
    def get(self, request, sort):
        sort = int(sort)
        commission_type = CommissionType.objects.get(id=sort)
        serializer = Commission_Type_Get_Serializer(instance=commission_type)

        return Response(serializer.data['commissions'], status=status.HTTP_200_OK)

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
    def post(self, request, sort):
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
            ).filter(name__contains=w).filter(commission_type_id=sort).order_by('-create_time')
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


class Commission_Type_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取所有类别的名字和id以及image',
        # manual_parameters=[ids],
        responses={200: type_simple_get_response}
    )
    def get(self, request):
        commission_type_list = CommissionType.objects.all()

        serializer = Commission_Type_Simple_Get_Serializer(instance=commission_type_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='添加单个类别',
        request_body=Commission_Type_Serializer,
        responses={201: 'Created'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data_dict = request.data
        serializer = Commission_Type_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Commission_Type_One_View(APIView):

    @swagger_auto_schema(
        operation_summary='获取单个类别',
        operation_description=
        """
            tag_activities 为 相关活动 列表
            包含每个活动的所有详细信息， 以 dict 表示， 表示同activity表示

        """,
        responses={200: 'ok'}
    )
    def get(self, request, id):
        params = request.query_params

        commission_type = CommissionType.objects.get(id=id)

        serializer = Commission_Type_Simple_Get_Serializer(instance=commission_type)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='修改单个类别',
        operation_description='根据id',
        request_body=Commission_Type_Serializer,
        responses={201: 'ok'}
    )
    def put(self, request, id):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data_dict = request.data
        # params = request.query_params
        if data_dict['image'].startswith('http') or data_dict['image'] == '':
            data_dict.pop('image')

        commission_type = CommissionType.objects.get(id=id)

        serializer = Commission_Type_Serializer(instance=commission_type, data=data_dict)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='删除单个委托类别',
        operation_description='根据委托类别名筛选删除',
        responses={204: 'NO'}
    )
    def delete(self, request, id):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        commission_type = CommissionType.objects.get(id=id)

        commission_type.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
