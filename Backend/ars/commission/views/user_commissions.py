from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from ars.commission.serializers.commission_get_serializers import Commission_Get_Serializer
from ars.models import *


class User_Create_Commissions(APIView):

    @swagger_auto_schema(
        operation_summary='用户委托',
        responses={200: 'OK', 400: '用户不存在'}
    )
    def get(self, request, id):
        user_id = id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = user.create_commissions.filter(audit=Commission.AuditStatusChoice.审核通过)

        serializer = Commission_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class User_Create_Commissions_Self(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='用户委托',
        responses={200: 'OK', 400: '用户不存在'}
    )
    def get(self, request, id):
        user_id = id
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = user.create_commissions.filter(audit=Commission.AuditStatusChoice.审核通过)

        serializer = Commission_Get_Serializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
