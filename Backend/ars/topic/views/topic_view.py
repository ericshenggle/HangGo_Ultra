
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from ars.topic.serializers.topic_change_serializer import *
from ars.topic.serializers.topic_get_extra_serializers import Topic_Comment_Get_Serializer

from ars.topic.serializers.topic_get_serializer import *
from ars.activity.serializers.activity_get_extra_serializers import *
from ars.models import *

from ars.activity.act_util import change_Activity_format
from ars.notification.wxapi import send_topic_in_audit
from ars.topic.serializers.topic_serializer import Topic_Serializer
from ars.topic.topic_util import change_Topic_format

debug = False

class Normal_Topic_Basic_View(APIView):

    @swagger_auto_schema(
        # manual_parameters = ['name_2','name'],
        # request_body = ActivityInfo_Serializer,
        # query_serializer=ActivitySerializer,
        responses={201: 'Created'}
    )
    def post(self, request, data_dict):
        user_id = request.user.id
        if debug:
            user_id = 1
        elif user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # _user = User
        # import pdb; pdb.set_trace()
        # data_dict = request.data
        # try:
        #     data_dict['start_at'] = change_data_time_format(data_dict['start_at'])
        #     data_dict['end_at'] = change_data_time_format(data_dict['end_at'])
        # except ValueError:
        #     return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)
        topic_data = dict(data_dict.pop('topic'))
        topic_data['audit'] = Topic.AuditStatusChoice.审核通过
        topic_data['description'] = data_dict['description']
        topic_data['create_at'] = datetime.now()   #.strftime('"%Y/%m/%d %H:%M')

        topic_type = TopicType.objects.get(name=topic_data['topic_type'])
        topic_data['topic_type'] = topic_type.id
        re_activity = Topic_Change_Serializer(data=topic_data)
        if re_activity.is_valid(raise_exception=False):
            re_activity.save()
            re_activity_d = re_activity.data
            data_dict['topic'] = re_activity_d['id']
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TopicInfo_Change_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            top_ = Topic.objects.get(id=data_dict['topic'])
            top_.delete()
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        top = Topic.objects.get(id=data_dict['topic'])
        Notification(
            user=request.user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.话题,
            topic = top,
            content='发布成功，自动审核通过，后续请查收相应审核状态',
            isread=False
        ).save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class Topic_All_View(APIView):

    @swagger_auto_schema(
        operation_summary='获取所有话题',
        operation_description=
        '''
        详细请看补充文档 话题查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK'}
    )
    # @api_view(['GET', 'PUT', 'POST', 'DELETE'])
    def get(self, request):
        params = request.query_params

        topic_list = Topic.objects.all().filter(audit=Topic.AuditStatusChoice.审核通过).order_by('-create_at')
        serializer = Topic_Get_Serializer(instance=topic_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='发布话题',
        operation_description=
        '''
        详细请看补充文档 话题发布 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={201: 'Created', 400: '错误提示消息', 404: '用户不存在'}
    )
    def post(self, request):
        user_id = request.user.id
        if debug:
            user_id = 1
        elif user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        authority = user.authority
        if authority[0] == '0':
            return Response('当前用户无发布话题权限，请及时进行申诉', status=status.HTTP_400_BAD_REQUEST)
        try:
            data_dict = change_Topic_format(request)
        except KeyError:
            return Response('您未填写完所有信息', status=status.HTTP_400_BAD_REQUEST)

        #data_dict['topic']['create_user'] = request.user.id
        data_dict['topic']['create_user'] = user.id
        ######################
        # if 'photo' in data_dict['activity']:
        #     data_dict['activity']['photo'] = request.data['photo']
        # if 'start_class' in data_dict:
        # return Lecture_Basic_View().post(request)
        # else:
        return Normal_Topic_Basic_View().post(request, data_dict)


class Topic_One_View(APIView):
    @swagger_auto_schema(
        operation_summary='获取单个话题',
        operation_description=
        '''
        详细请看补充文档 话题查看 接口
        https://devcloud.cn-north-4.huaweicloud.com/codehub/project/86143c7a873546d5bcdddbc65c298cd1/codehub/872787/file?ref=master&path=%25E6%258E%25A5%25E5%258F%25A3%25E8%25A1%25A5%25E5%2585%2585%25E8%25AF%25B4%25E6%2598%258E.md
        ''',
        responses={200: 'OK', 404: '没有该话题'}
    )
    def get(self, request, id):
        params = request.query_params
        try:
            topic = Topic.objects.get(id=id)
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_id = request.user.id
        if user_id is None:
            user_id = 1
        user = User.objects.get(id=user_id)
        serializer = Topic_Comment_Get_Serializer(instance=topic, context={'user': user})


        click = ClickRecord_Topic(
            topic_id=id, user_id=user_id
        )
        click.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary='删除单个话题',
        operation_description='根据id删除话题',
        responses={204: 'OK', 400: '错误信息', 404: '用户不存在'}
    )
    def delete(self, request, id):
        if id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_id = request.user.id
        if debug:
            user_id = 1
        elif user_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            topic = Topic.objects.get(id=id)
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        if user_id == 1:
            Notification(
                user=topic.create_user,
                not_type=Notification.NotificationType.系统通知,
                type=Notification.Type.话题,
                topic=topic,
                content='您发布的话题 {} 被删除'.format(topic.name),
                isread=False
            ).save()
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='修改话题审核',
        responses={200: 'OK', 400: '错误信息', 403: '没有权限', 404: '用户不存在'}
    )
    def put(self, request, id):
        if id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user_id != 1:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            topic = Topic.objects.get(id=id)
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        topic_data = {}
        topic_data['audit'] = request.data['audit']
        # activity_serializer = Topic_Serializer(instance=topic, data=topic_data)
        # if activity_serializer.is_valid():
        #     activity_serializer.save()
        # else :
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        Topic.objects.filter(id=id).update(audit=2)
        topic_serializer = Topic_Serializer(instance=topic)
        Notification(
            user=topic.create_user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.话题,
            topic=topic,
            content='您发布的话题 {} 审核状态被更改'.format(topic.name),
            isread=False
        ).save()
        return Response(topic_serializer.data, status=status.HTTP_200_OK)

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
