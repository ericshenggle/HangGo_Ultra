from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ars.commission.com_util import verify_commission, verify_null
from ars.commission.serializers.commission_get_serializers import Commission_Get_Serializer
from ars.commission.serializers.commission_publish_serializers import Commission_Publish_Serializer
from ars.commission.serializers.commission_get_detail_serializers import Commission_Get_Detail_Serializer
from ars.commission.serializers.commission_change_serializers import Commission_Change_Serializer
from ars.models import *
from ars.utils import change_data_time_format


class Commission_Publish_view(APIView):
    @swagger_auto_schema(
        operation_summary='发布委托',
        operation_description=
        '''
            {
                "commission_type_id": bigint,
                "name": text,
                "start_time": str,
                "end_time": str,
                "real_time": int,
                "location": int,
                "description": text,
                "fee": int,
                "tags":['新主楼',...]
            }
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
        authority = user.authority
        if authority[2] == '0':
            return Response('当前用户无发布委托权限，请及时进行申诉', status=status.HTTP_400_BAD_REQUEST)
        data_dict = request.data.copy()
        try:
            verify_null(data_dict)
        except KeyError:
            return Response('您未填写完所有信息', status=status.HTTP_400_BAD_REQUEST)

        ver = verify_commission(data_dict)
        if 'error' in ver:
            return Response(ver['message'], status=status.HTTP_400_BAD_REQUEST)

        try:
            data_dict['start_time'] = change_data_time_format(
                data_dict['start_time'])
            data_dict['end_time'] = change_data_time_format(
                data_dict['end_time'])
        except ValueError:
            return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)

        data_dict['user'] = user_id
        tags_id = []
        tags_data = data_dict.pop('tags')
        for tag_data in tags_data:
            tag_data = dict(tag_data)
            tag = Tag.objects.get_or_create(**tag_data)[0]
            tags_id.append(tag.id)
        data_dict['tags'] = tags_id
        data_dict['audit'] = Commission.AuditStatusChoice.审核通过
        data_dict['status'] = Commission.PublicStatusChoice.已发布

        serializer = Commission_Publish_Serializer(data=data_dict)
        if serializer.is_valid(raise_exception=True):
            commission = serializer.save()
            Notification(
                user=user,
                not_type=Notification.NotificationType.系统通知,
                type=Notification.Type.委托,
                commission=commission,
                content='您发布的{}委托已生效'.format(commission.name),
                isread=False
            ).save()
            # TODO
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response('发布委托失败', status=status.HTTP_400_BAD_REQUEST)



class Commission_Check_view(APIView):
    @swagger_auto_schema(
        operation_summary='查看当前用户已发布的委托',
        responses={200: 'OK', 404: '用户不存在'}
    )
    def get(self, request, Status):
        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        Status = int(Status)
        commission_list = user.create_commissions.filter(audit=Status).order_by('-create_time')
        serializer = Commission_Get_Serializer(instance=commission_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Commission_Change_view(APIView):

    def getNew(self, id):
        try:
            commission = Commission.objects.get(id=id)
        except Commission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = Commission_Get_Detail_Serializer(instance=commission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='修改已发布委托',
        operation_description=
        '''
        允许用户修改除user, type, tag, comment外所有字段信息
        修改时需要get到所需修改的委托，再将相应字段修改（其余字段保留），再发回后端进行修改
        ''',
        responses={201: 'Created', 400: '错误提示消息', 404: '用户不存在'}
    )
    def post(self, request):
        data_dict = request.data.copy()
        try:
            commission = Commission.objects.get(id=data_dict['id'])
        except Commission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user_id != commission.user.id:
            return Response('你不是该委托的创建者, 不能进行修改', status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verify_null(data_dict)
        except KeyError:
            return Response('缺少字段', status=status.HTTP_400_BAD_REQUEST)

        ver = verify_commission(data_dict)
        if 'error' in ver:
            return Response(ver['message'], status=status.HTTP_400_BAD_REQUEST)

        try:
            data_dict['start_time'] = change_data_time_format(
                data_dict['start_time'])
            data_dict['end_time'] = change_data_time_format(
                data_dict['end_time'])
        except ValueError:
            return Response('时间格式有问题', status=status.HTTP_400_BAD_REQUEST)

        serializer = Commission_Change_Serializer(instance=commission, data=data_dict)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您发布的{}委托已被修改'.format(commission.name),
            isread=False
        ).save()
        return self.getNew(data_dict['id'])

    @swagger_auto_schema(
        operation_summary='删除已发布委托',
        operation_description=
        '''
            {
                "commission_id": int
            }
        ''',
        responses={204: 'OK', 400: '错误提示消息', 404: '用户不存在'}
    )
    def delete(self, request):
        data = request.data
        try:
            commission = Commission.objects.get(id=data['commission_id'])
        except Commission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_id = request.user.id
        if user_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user_id != commission.user.id:
            return Response('你不是该委托的创建者, 不能进行删除', status=status.HTTP_400_BAD_REQUEST)

        Notification(
            user=user,
            not_type=Notification.NotificationType.系统通知,
            type=Notification.Type.委托,
            commission=commission,
            content='您发布的{}委托已被删除'.format(commission.name),
            isread=False
        ).save()
        commission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
