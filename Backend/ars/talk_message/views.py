from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.talk_message.serializers import TalkMessageSerializer


class MyMessage(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='获取所有目标为本用户的未读聊天消息',
        responses={200: '获取成功'},
    )
    def get(self, request):
        user = request.user
        messages = user.received_messages.all().filter(is_read=False)
        serializer = TalkMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
