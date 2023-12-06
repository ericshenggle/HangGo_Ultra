from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.models import User
from ars.user.serializers import UserPublicSerializer


class Followees(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='新关注用户',
        responses={200: '成功', 404: '目标用户不存在'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "follow_user": openapi.Schema(type=openapi.TYPE_INTEGER, description='要关注的用户的ID'),
            },
        ),
    )
    def post(self, request):
        if 'follow_user' not in request.data:
            return Response(data={'detail': '缺失目标用户'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(pk=request.data.get('follow_user'))
        except User.DoesNotExist:
            return Response(data={'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        user.followers.add(target_user)
        user.save()
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='取关用户',
        responses={204: '成功', 404: '目标用户不存在', '400': '缺失目标用户字段'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "follow_user": openapi.Schema(type=openapi.TYPE_INTEGER, description='要取关的用户的ID'),
            },
        ),
    )
    def delete(self, request):
        if 'follow_user' not in request.data:
            return Response(data={'detail': '缺失目标用户'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(pk=request.data.get('follow_user'))
        except User.DoesNotExist:
            return Response(data={'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        user.followers.remove(target_user)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='得到该用户关注的所有用户',
        responses={200: '成功'}
    )
    def get(self, request):
        user_set = request.user.followers
        serializer = UserPublicSerializer(user_set, many=True, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Followers(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='得到所有关注该用户用户',
        responses={200: '成功'},
    )
    def get(self, request):
        user_set = request.user.followees
        serializer = UserPublicSerializer(user_set, many=True, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
