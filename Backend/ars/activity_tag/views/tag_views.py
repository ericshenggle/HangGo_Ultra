from django.contrib.auth.models import User, Group
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.activity_tag.serializers.tag_serializers import * 
from ars.activity_tag.serializers.tag_get_serializers import *
from ars.models import *

# Create your views here.
tag_get_response = openapi.Response('response description', Tag_Get_Serializer)
tag_simple_get_response = openapi.Response('response description', Tag_Simple_Get_Serializer)      


ids = openapi.Parameter('id_list', in_=openapi.IN_QUERY, description='主键id列表',
                                            type=openapi.TYPE_INTEGER)

class Activity_Tag_Basic_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取所有标签',
        operation_description=
        """
            tag_activities 为 相关活动 列表
            包含每个活动的所有详细信息， 以 dict 表示， 表示同activity表示
            得到与GET请求活动信息内容一致
        """,
        responses={200: tag_get_response}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request):
        params = request.query_params

        tags = Tag.objects.all()

        serializer = Tag_Get_Serializer(instance=tags, many=True) 

        return Response(serializer.data,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='添加单个标签',
        request_body = Tag_Serializer,
        responses={201:'Created'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data_dict = request.data
        serializer = Tag_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Activity_Tag_One_View(APIView):

    @swagger_auto_schema(
        operation_summary='获取单个标签',
        operation_description=
        """
            tag_activities 为 相关活动 列表
            包含每个活动的所有详细信息， 以 dict 表示， 表示同activity表示
        
        """,
        responses={200: tag_get_response}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request, id):
        params = request.query_params

        tag = Tag.objects.get(id = id)

        serializer = Tag_Get_Serializer(instance=tag) 

        return Response(serializer.data,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='修改单个标签',
        request_body = Tag_Serializer,
        responses={201:'OK'}
    )
    def put(self, request, id):
        data_dict = request.data
        # params = request.query_params
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        tag = Tag.objects.get(id = id)

        serializer = Tag_Serializer(instance=tag, data=data_dict)

        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @swagger_auto_schema(
        operation_summary='删除单个活动标签',
        operation_description='根据活动标签id筛选删除',
        responses={204:'NO'}
    )
    def delete(self, request, id):
        # params = request.query_params
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        tag = Tag.objects.get(id = id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class Activity_Tag_List_View(APIView):
    @swagger_auto_schema(
        operation_summary='根据列表值获取一些类别',
        operation_description=
        """
            根据传进来的list id或name(两者选一) 获取tag对应的信息
            传输格式
            {
                "id": [...],
                "name": [...]
            }
        """,
        # manual_parameters=[ids],
        responses={200:tag_simple_get_response}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)        
        params = request.data
        if 'id' in params:
            id_list = params['id']
            tags_list = Tag.objects.filter(id__in=id_list)
        else:
            name_list = params['name']
            tags_list = Tag.objects.filter(name__in=name_list)           
        serializer = Tag_Simple_Get_Serializer(instance=tags_list, many=True) 

        return Response(serializer.data,status=status.HTTP_200_OK)