from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.activity_type.serializers.type_serializers import *
from ars.activity_type.serializers.type_get_serializers import *
from ars.models import *
import jieba
from ars.activity.views.recommend_views import recommend_View

class Activity_Message_View(APIView):
    @swagger_auto_schema(
        operation_summary='活动聊天',
        operation_description =
        """
        传入:{
            'content': ''//
        }
        返回活动列表
        """,
        responses={200:'OK'}
    )
    def post(self, request):
        content = request.data.get('content', "")
        message = "您好"
        if content == "你好" or content == "您好":
            pass
        elif "活动" in content:
            return recommend_View().post(request)
        else :
            message = "对不起，我无法理解您的问题"
        return Response(message, status=status.HTTP_200_OK)


    def get_activity_serializer(self, content):
        # words = jieba.lcut(content)
        # if content.contains
        
        activity_list = []
        serializer = Activity_Get_Serializer(data=activity_list)
        return serializer