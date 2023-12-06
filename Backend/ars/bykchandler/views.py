from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.bykchandler.update_selected import update_selected


class UpdateUserBykc(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='开启或者关闭博雅课程功能',
        responses={201: '成功', 400: '错误（错误信息位于detail中)，如果没有成功，is_active状态依旧为False'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否开启博雅课程支持'),
                "sso_password": openapi.Schema(type=openapi.TYPE_STRING,
                                               description='统一认证密码（如果is_active为False，这一项可以留空）')
            },
        ),
    )
    def post(self, request):
        is_active = request.data.get('is_active', False)
        sso_password = request.data.get('sso_password', '')
        user = request.user
        user.bykc_isactive = is_active
        user.sso_password = sso_password
        user.save()
        if user.bykc_isactive:
            try:
                update_selected(request.user)
            except RuntimeError as e:
                user.bykc_isactive = False
                user.save()
                return Response(data={'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


class UpdateBykc(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='立刻刷新用户的所有博雅课程',
        responses={201: '成功', 400: '错误：（错误信息位于detail中)'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
            },
        ),
    )
    def post(self, request):
        try:
            update_selected(request.user)
        except RuntimeError as e:
            return Response(data={'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
