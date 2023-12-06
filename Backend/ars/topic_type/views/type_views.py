from django.contrib.auth.models import User, Group
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.models import *

# Create your views here.
from ars.topic_type.serializers.type_get_serializers import Topic_Type_Get_Serializer, Topic_Type_Simple_Get_Serializer
from ars.topic_type.serializers.type_serializers import Topic_Type_Serializer
from ars.topic_type.serializers.type_serializers import To_Type_Serializer

type_get_response = openapi.Response('response description', Topic_Type_Get_Serializer)
type_simple_get_response = openapi.Response('response description', Topic_Type_Simple_Get_Serializer)
ids = openapi.Parameter('id_list', in_=openapi.IN_QUERY, description='主键id列表',
                                            type=openapi.TYPE_INTEGER)
DEBUG = False



class Topic_Type_Basic_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取所有类别',
        operation_description=
        """
            tag_activities 为 相关活动 列表
            包含每个活动的所有详细信息， 以 dict 表示， 表示同activity表示
            得到与GET请求活动信息内容一致
        """,
        responses={200:type_get_response}
    )
    def get(self, request):
        activity_type_list = TopicType.objects.all()
        serializer = Topic_Type_Get_Serializer(instance=activity_type_list, many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='添加单个类别',
        request_body=To_Type_Serializer,
        responses={201: 'Created'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        data_dict = request.data
        serializer = To_Type_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Topic_Type_One_View(APIView):

    @swagger_auto_schema(
        operation_summary='获取单个类别',
        operation_description=       
        """
            tag_activities 为 相关活动 列表
            包含每个活动的所有详细信息， 以 dict 表示， 表示同activity表示
        
        """,
        responses={200:type_get_response}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request, id):
        activity_type = TopicType.objects.get(id=id)
        serializer = Topic_Type_Get_Serializer(instance=activity_type)

        return Response(serializer.data,status=status.HTTP_200_OK)

    

    @swagger_auto_schema(
        operation_summary='删除单个话题类别',
        responses={204: 'NO'}
    )
    def delete(self, request, id):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        topic_type = TopicType.objects.get(id=id)

        topic_type.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='修改单个类别',
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

        topic_type = TopicType.objects.get(id=id)

        serializer = To_Type_Serializer(instance=topic_type, data=data_dict)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class Topic_Type_List_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取所有类别的名字和id',
        # manual_parameters=[ids],
        responses={200: type_simple_get_response}
    )
    def get(self, request):
        activity_type_list = TopicType.objects.all()

        serializer = Topic_Type_Simple_Get_Serializer(instance=activity_type_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(
    #     operation_summary='根据列表值获取一些类别',
    #     operation_description=
    #     """
    #         根据传进来的list id或name(两者选一) 获取type对应的信息
    #         传输格式
    #         {
    #             "id": [...],
    #             "name": [...]
    #         }
    #     """,
    #     # manual_parameters=[ids],
    #     responses={200:type_simple_get_response}
    # )
    # # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    # def post(self, request):
    #     user_id = request.user.id
    #     if user_id is None:
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)
    #     params = request.data
    #     if 'id' in params:
    #         id_list = params['id']
    #         activity_type_list = ActivityType.objects.filter(id__in=id_list)
    #     else:
    #         name_list = params['name']
    #         tags_list = ActivityType.objects.filter(name__in=name_list)
    #
    #     serializer = Activity_Type_Simple_Get_Serializer(instance=activity_type_list, many=True)
    #
    #     return Response(serializer.data,status=status.HTTP_200_OK)

# class Activity_Type_User_Basic_View(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_summary='获取所有类别',
#         operation_description=
#         """
#             用户相关
#             返回 {
#                 "name":, "id":, "is_subscribe": //是否订阅
#             }
#         """,
#         responses={200:'OK', 404:'用户不存在'}
#     )
#     # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
#     def get(self, request):
#         params = request.query_params
#         user_id = request.user.id
#         if user_id is None:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         activity_type_list = ActivityType.objects.all()
#
#         serializer = Activity_Type_User_Get_Serializer(
#             instance=activity_type_list, many=True,
#             context={'user_id':user_id}
#         )
#         return Response(serializer.data,status=status.HTTP_200_OK)




