import datetime

import pytz
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import *

from ars.bykchandler.update_selected import update_selected
from ars.bykchandler.utils import post_api
from ars.models import *
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

openid_activity_type_id = openapi.Parameter('activity_type_id', in_=openapi.IN_QUERY, description='Activity_type的ID',
                                            type=openapi.TYPE_INTEGER)


class Subscribe(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='订阅活动类别',
        responses={201: '活动类别订阅成功', 400: '缺失id', 404: '目标不存在'},
        manual_parameters=[openid_activity_type_id]
    )
    def post(self, request):
        if 'activity_type_id' not in request.data:
            return Response(data={'detail': '缺失id'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        activity_type = get_object_or_404(ActivityType, pk=request.data['activity_type_id'])
        user.subscribe_activity_types.add(activity_type)
        user.save()
        return Response(data={'message': '活动类别订阅成功'}, status=status.HTTP_201_CREATED)


class CancelSubscribe(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='取消订阅活动类别',
        responses={204: '取消活动类别订阅成功', 400: '缺失id', 404: '目标不存在'},
        manual_parameters=[openid_activity_type_id]
    )
    def post(self, request):
        if 'activity_type_id' not in request.data:
            return Response(data={'detail': '缺失id'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        activity_type = get_object_or_404(ActivityType, pk=request.data['activity_type_id'])
        user.subscribe_activity_types.remove(activity_type)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SelectActivity(APIView):
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #   operation_summary='用户新增订阅活动类别'
    # )

    # @swagger_auto_schema(
    #    operation_summary='选择活动',
    #    responses={201: '活动选择成功'}
    # )
    openapi_activity_id = openapi.Parameter('activity_id', in_=openapi.IN_QUERY, description='Activity的ID',
                                            type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(
        operation_summary='选择活动',
        responses={201: '活动选择成功', 400: '缺失id或者报名人数已满或者不在报名时间', 404: '目标不存在'},
        manual_parameters=[openapi_activity_id]
    )
    def post(self, request):
        if 'activity_id' not in request.data:
            return Response(data={'detail': '缺失id'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        activity = get_object_or_404(Activity, pk=request.data['activity_id'])
        if activity.normal_activity.count() != 0:
            if activity.normal_activity.get().allow_total <= activity.attend_users.count() and activity.activity_type_id != 9:
                return Response(data={'detail': '人数已满'}, status=status.HTTP_400_BAD_REQUEST)
            if activity.start_enrollment_at > datetime.datetime.now():
                return Response(data={'detail': '活动还没有开始报名'}, status=status.HTTP_400_BAD_REQUEST)
            if activity.end_enrollment_at < datetime.datetime.now():
                return Response(data={'detail': '活动已经结束报名'}, status=status.HTTP_400_BAD_REQUEST)
        if activity.activity_type_id == 9:
            if user.bykc_isactive:
                try:
                    token, session = update_selected(user)
                    post_api(session, token, user.student_id, user.sso_password, "choseCourse",
                             {"courseId": activity.bykc_id})
                except RuntimeError as e:
                    return Response(data={'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'detail': '您没有开启博雅功能，请在设置页面开启'}, status=status.HTTP_400_BAD_REQUEST)
        user.attend_activities.add(activity)
        user.save()
        return Response(data={'detail': '活动选择成功'}, status=status.HTTP_201_CREATED)


class CancelSelectActivity(APIView):
    permission_classes = [IsAuthenticated]
    openapi_activity_id = openapi.Parameter('activity_id', in_=openapi.IN_QUERY, description='Activity的ID',
                                            type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(
        operation_summary='取消选择活动',
        responses={204: '活动取消选择成功', 400: '缺失id或者不在报名时间', 404: '目标不存在'},
        manual_parameters=[openapi_activity_id]
    )
    def post(self, request):
        if 'activity_id' not in request.data:
            return Response(data={'detail': '缺失id'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        activity = get_object_or_404(Activity, pk=request.data['activity_id'])
        if activity.normal_activity.count() != 0:
            if activity.end_enrollment_at < datetime.datetime.now():
                return Response(data={'detail': '活动选课已经结束'}, status=status.HTTP_400_BAD_REQUEST)
        if activity.activity_type_id == 9:
            if user.bykc_isactive:
                try:
                    token, session = update_selected(user)
                    post_api(session, token, user.student_id, user.sso_password, "delChosenCourse",
                             {"id": activity.bykc_id})
                except RuntimeError as e:
                    return Response(data={'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'detail': '您没有开启博雅功能，请在设置页面开启'}, status=status.HTTP_400_BAD_REQUEST)
        user.attend_activities.remove(activity)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemarkActivity(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='为活动评分',
        responses={400: '评分不合法', 404: '活动不存在或者用户没有选择活动', 201: '评分成功'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "activity_id": openapi.Schema(type=openapi.TYPE_INTEGER, description='activity_id'),
                "remark": openapi.Schema(type=openapi.TYPE_INTEGER,
                                         description='评分（1-5之间的整数）')
            },
        ),
    )
    def post(self, request):
        try:
            activity = Activity.objects.get(pk=request.data.get('activity_id', ''))
            user_activity = UserActivity.objects.get(user=request.user, activity=activity)
        except Activity.DoesNotExist or UserActivity.DoesNotExist:
            return Response(data={'detail': '活动不存在或者用户没有选课'}, status=status.HTTP_404_NOT_FOUND)
        uremark = request.data.get('remark')
        if 1 <= uremark <= 5:
            user_activity.remark = uremark
            user_activity.save()
        else:
            return Response(data={'detail': '评分不合法'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
