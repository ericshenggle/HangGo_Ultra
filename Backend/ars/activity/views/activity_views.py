from django.contrib.auth.models import User, Group
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.activity.serializers.activity_info_serializer import ActivityInfo_Serializer
from ars.activity.serializers.activity_serializers import *
from ars.activity.serializers.activity_change_serializers import *
from ars.activity.serializers.activity_get_serializer import *
from ars.activity.serializers.activity_get_extra_serializers import *
# from ars.activity.serializers.lecture_serializer import Lecture_Serializer
from ars.activity_type.serializers import *
from ars.models import *

from ars.utils import change_data_time_format
from ars.activity.act_util import change_Activity_format, verify_activity
from datetime import datetime
from ars.notification.wxapi import send_activity_in_audit


class Normal_Activity_Basic_View(APIView):

    @swagger_auto_schema(
        # manual_parameters = ['name_2','name'],
        # request_body = ActivityInfo_Serializer,
        # query_serializer=ActivitySerializer,
        responses={201: 'Created'}
    )
    def post(self, request, data_dict):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # _user = User
        # import pdb; pdb.set_trace()
        # data_dict = request.data
        # try:
        #     data_dict['start_at'] = change_data_time_format(data_dict['start_at'])
        #     data_dict['end_at'] = change_data_time_format(data_dict['end_at'])
        # except ValueError:
        #     return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)
        activity_data = dict(data_dict.pop('activity'))
        activity_data['audit_status'] = Activity.AuditStatusChoice.审核中
        activity_data['public_status'] = Activity.PublicStatusChoice.已提交审核
        tags_data = activity_data.pop('tags')
        activity_type_data = dict(activity_data.pop('activity_type'))

        tags = []
        tags_id = []
        for tag_data in tags_data:
            tag_data = dict(tag_data)
            tag = Tag.objects.get_or_create(**tag_data)[0]
            tags.append(tag)
            tags_id.append(tag.id)
        activity_type = ActivityType.objects.get(name=activity_type_data['name'])
        activity_type_id = activity_type.id

        activity_data['tags'] = tags_id
        activity_data['activity_type'] = activity_type_id
        re_activity = Activity_Change_Serializer(data=activity_data)
        if re_activity.is_valid(raise_exception=False):
            re_activity.save()
            re_activity_d = re_activity.data
            data_dict['activity'] = re_activity_d['id']
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ActivityInfo_Change_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            act_ = Activity.objects.get(id=data_dict['activity'])
            act_.delete()
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        act = Activity.objects.get(id=data_dict['activity'])
        send_activity_in_audit(act)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Normal_Activity_One_View(APIView):

    @swagger_auto_schema(
        request_body=ActivityInfo_Serializer,
        responses={201: 'Created', 400: 'Error'}
    )
    def put(self, request, activity, data_dict):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # try:
        #     request.data['start_at'] = change_data_time_format(data_dict['start_at'])
        #     request.data['end_at'] = change_data_time_format(data_dict['end_at'])
        # except ValueError:
        #     return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)
        # params = request.query_params
        # data_dict = request.data
        if 'activity' in data_dict:
            data_dict.pop('activity')
        # normal_activity = ActivityInfo.objects.get(id = id)
        normal_activity = activity.normal_activity.all().first()

        serializer = ActivityInfo_Serializer(instance=normal_activity, data=data_dict)

        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='删除单个活动',
        operation_description='根据 活动名筛选删除',
        responses={204: 'NO'}
    )
    def delete(self, request, activity):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        params = request.query_params

        normal_activity = activity.normal_activity.all().first()
        normal_activity.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class Activity_All_View(APIView):

    @swagger_auto_schema(
        operation_summary='获取所有审核通过活动',
        operation_description=
        '''
        详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK'}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request):
        params = request.query_params

        activity_list = Activity.objects.exclude(activity_type__id=9) \
            .filter(audit_status=Activity.AuditStatusChoice.审核通过)
        serializer = Activity_Get_Serializer(instance=activity_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='发布活动',
        operation_description=
        '''
        详细请看补充文档 活动发布 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={201: 'Created', 400: '错误提示消息', 404: '用户不存在'}
    )
    def post(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            data_dict = change_Activity_format(request)
        except KeyError:
            return Response('您未填写完所有信息', status=status.HTTP_400_BAD_REQUEST)

        try:
            int(data_dict['allow_total'])
        except ValueError:
            return Response('人数填写错误', status=status.HTTP_400_BAD_REQUEST)

        ver = verify_activity(data_dict)
        if 'error' in ver:
            return Response(ver['message'], status=status.HTTP_400_BAD_REQUEST)

        if int(data_dict['allow_total']) <= 0:
            return Response('人数错误', status=status.HTTP_400_BAD_REQUEST)

        data_dict['activity']['create_user'] = request.user.id
        ######################
        # if 'photo' in data_dict['activity']:
        #     data_dict['activity']['photo'] = request.data['photo']
        try:
            data_dict['activity']['start_enrollment_at'] = change_data_time_format(
                data_dict['activity']['start_enrollment_at'])
            data_dict['activity']['end_enrollment_at'] = change_data_time_format(
                data_dict['activity']['end_enrollment_at'])
            data_dict['start_at'] = change_data_time_format(data_dict['start_at'])
            data_dict['end_at'] = change_data_time_format(data_dict['end_at'])
        except ValueError:
            return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)
        # if 'start_class' in data_dict:
        # return Lecture_Basic_View().post(request)
        # else:
        return Normal_Activity_Basic_View().post(request, data_dict)


class Activity_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取单个活动',
        operation_description=
        '''
        详细请看补充文档 活动查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK', 404: '没有该活动'}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request, id):
        params = request.query_params
        try:
            activity = Activity.objects.get(id=id)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_id = request.user.id
        if user_id is None:
            user_id = 1
        user = User.objects.get(id=user_id)
        serializer = Activity_Comment_Get_Serializer(instance=activity, context={'user': user})

        click = ClickRecord(
            activity_id=id, user_id=user_id
        )
        click.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='修改单个活动',
        operation_description=
        '''
        允许用户修改除user，type，tag外所有字段信息
        修改时需要get到所需修改的活动，再将相应字段修改（其余字段保留），再发回后端进行修改
        ''',
        # request_body = ActivityInfo_Serializer,
        responses={201: 'Created', 400: '错误信息', 404: '用户不存在'}
    )
    def put(self, request, id):
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            data_dict = change_Activity_format(request)
        except KeyError:
            return Response('您发布活动缺少字段问题', status=status.HTTP_400_BAD_REQUEST)
        # data_dict['activity']['create_user'] = request.user.id
        ######################
        # if 'photo' in data_dict['activity']:
        #     data_dict['activity']['photo'] = request.data['photo']

        try:
            int(data_dict['allow_total'])
        except ValueError:
            return Response('人数填写错误', status=status.HTTP_400_BAD_REQUEST)

        try:
            data_dict['activity']['start_enrollment_at'] = change_data_time_format(
                data_dict['activity']['start_enrollment_at'])
            data_dict['activity']['end_enrollment_at'] = change_data_time_format(
                data_dict['activity']['end_enrollment_at'])
            data_dict['start_at'] = change_data_time_format(data_dict['start_at'])
            data_dict['end_at'] = change_data_time_format(data_dict['end_at'])
        except ValueError:
            return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)

        ver = verify_activity(data_dict)

        if 'error' in ver:
            return Response(ver['message'], status=status.HTTP_400_BAD_REQUEST)

        if 'activity' in data_dict:
            activity_data = dict(data_dict.pop('activity'))
        activity_data['audit_status'] = Activity.AuditStatusChoice.审核中

        # if 'activity_type' in activity_data:
        #     activity_data.pop('activity_type')
        # if 'tags' in activity_data:
        #     activity_data.pop('tags')
        try:
            activity = Activity.objects.get(id=id)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if activity.create_user.id != user_id:
            return Response('不为创建人', status=status.HTTP_400_BAD_REQUEST)

        if int(data_dict['allow_total']) <= 0:
            return Response('人数错误', status=status.HTTP_400_BAD_REQUEST)
        else:
            nnn = len(activity.attend_users.all())
            if nnn > int(data_dict['allow_total']):
                return Response('人数错误，应不小于已参与人数', status=status.HTTP_400_BAD_REQUEST)

        activity_type_data = dict(activity_data.pop('activity_type'))
        activity_type = ActivityType.objects.get(name=activity_type_data['name'])
        activity_type_id = activity_type.id

        activity_data['activity_type'] = activity_type_id

        activity_serializer = Activity_Serializer(instance=activity, data=activity_data)
        if activity_serializer.is_valid(raise_exception=False):
            activity_serializer.save()
        ret = Normal_Activity_One_View().put(request, activity, data_dict)

        return ret

    @swagger_auto_schema(
        operation_summary='删除单个活动',
        operation_description='根据id删除活动',
        responses={204: 'OK', 400: '错误信息', 404: '用户不存在'}
    )
    def delete(self, request, id):
        if id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            activity = Activity.objects.get(id=id)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        activity.delete()
        # if len(activity.normal_activity.all()) != 0:
        #     Normal_Activity_One_View().delete(request, activity)
        # else:
        #     Lecture_One_View().delete(request, activity)
        return Response(status=status.HTTP_204_NO_CONTENT)


'''
class Lecture_Basic_View(APIView):

    @swagger_auto_schema(
        # manual_parameters = ['name_2','name'],
        request_body = Lecture_Serializer,
        # query_serializer=ActivitySerializer,
        responses={201:'Created'}
    )
    def post(self, request):
        data_dict = request.data
        activity_data = dict(data_dict.pop('activity'))

        tags_data = activity_data.pop('tags')
        activity_type_data = dict(activity_data.pop('activity_type'))

        tags = []
        tags_id = []
        for tag_data in tags_data:
            tag_data = dict(tag_data)
            tag = Tag.objects.get_or_create(**tag_data)[0]
            tags.append(tag)
            tags_id.append(tag.id)
        activity_type = ActivityType.objects.get(name=activity_type_data['name'])
        activity_type_id = activity_type.id

        activity_data['tags'] = tags_id
        activity_data['activity_type'] = activity_type_id

        re_activity = Activity_Change_Serializer(data=activity_data)
        if re_activity.is_valid(raise_exception=True):
            re_activity.save()
            re_activity = re_activity.data
            data_dict['activity'] = re_activity['id']
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        serializer = Lecture_Change_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Lecture_One_View(APIView):

    @swagger_auto_schema(
        request_body = Lecture_Serializer,
        responses={201:'Created', 400: 'Error'}
    )
    def put(self, request, activity):
        data_dict = request.data
        params = request.query_params
        if 'activity' in data_dict:
            data_dict.pop('activity')
        # lecture = LectureInfo.objects.get(id = id)
        lecture = activity.lecture.all().first()

        serializer = Lecture_Serializer(instance = lecture, data=data_dict)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @swagger_auto_schema(
        operation_summary='删除单个活动',
        operation_description='根据 活动名筛选删除',
        responses={204:'NO'}
    )
    def delete(self, request, activity):
        params = request.query_params

        # activity = LectureInfo.objects.get(id = id).delete()
        lecture = activity.lecture.all().first()
        lecture.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
'''
