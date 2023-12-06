import random
from django.core.mail import send_mail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ars.custom_permissions.custom_permissions import IsSelfUser
from django.http import JsonResponse
from rest_framework.decorators import action

from ars.notification.wxapi import send_user_in_audit, send_user_audit_success
from ars.utils import code2session
from ars.models import User, EmailVerification
from ars.user.serializers import UserSerializer, UserPublicSerializer, EmailVerificationSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions


class UserViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'register' or self.action == 'post_partial_update':
            serializer_class = UserSerializer
        else:
            serializer_class = UserPublicSerializer
        return serializer_class

    def get_permissions(self):
        if self.action == 'register' or self.action == 'get_email_verification':
            permission_classes = []
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsSelfUser]
        elif self.action == 'profile' or self.action == 'post_partial_update':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'info':
            permission_classes = []
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=True)
    def info(self, request, pk=None):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserPublicSerializer(target_user, many=False,
                                          context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='获取当前用户的个人信息',
        manual_parameters=[],
        responses={200: UserSerializer(many=False)}
    )
    @action(methods=['get'], detail=False)
    def profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def post_partial_update(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    openid_email = openapi.Parameter('email', in_=openapi.IN_QUERY, description='用户请求验证的邮箱地址',
                                     type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        operation_summary='发送验证邮件',
        operation_description='在用户注册页面中，设置一个“获取验证邮件”按钮，点击后调用此接口向用户邮箱发送验证邮件',
        responses={200: '邮件发送成功', 400: '无效请求'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description='用户输入的电子邮箱')
            },
        ),
    )
    @action(methods=['post'], detail=False)
    def get_email_verification(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                User.objects.get(email=serializer.validated_data['email'])
            except User.DoesNotExist:
                target, answer = EmailVerification.objects.get_or_create(email=serializer.validated_data['email'])
                target.verify_code = random.randint(100000, 999999)
                target.save()
                send_mail(subject='您的北航大学生活动中心注册邮箱确认', message="您好，感谢您的注册！您的验证码为" + str(target.verify_code),
                          recipient_list=[target.email], fail_silently=False,from_email=None)
                msg = '发送成功'
                return JsonResponse({'detail': msg}, status=status.HTTP_200_OK)
            return JsonResponse({'detail': '邮箱地址已占用'}, status=status.HTTP_400_BAD_REQUEST)
            # 向用户发送邮件：
        else:
            msg = '无效邮箱地址'
            return JsonResponse({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

    def do_register(self, data, response):
        data['openid'] = response['openid']
        data['username'] = data['email']
        create_serializer = UserSerializer(data=data)
        if create_serializer.is_valid():
            user = User(**create_serializer.validated_data)
            user.is_active = False
            user.audit_status = User.AuditStatus.审核中
            user.username = user.email
            if user.email.endswith('@buaa.edu.cn'):
                user.is_active = True
                user.audit_status = User.AuditStatus.已通过
            user.save()
            create_serializer = UserSerializer(user)
            if not user.is_active:
                send_user_in_audit(user)
            else:
                send_user_audit_success(user)
            return Response(create_serializer.data, status=status.HTTP_201_CREATED)
        return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='用户注册（提交审核）',
        operation_description='将下表中的参数（基本都是小程序直接调用获取用户信息接口）配上wx.login中得到的code : xxx以及post /users/get_email_verification之后得到从邮箱中收到的email_verification_code:xxx，不需要发送下表中的openid字段。此外，将要发送的证明文件的key设置为credential（文档插件出了点乌龙，稍后修改）'
    )
    @action(methods=['post'], detail=False)
    def register(self, request):
        if 'code' in request.data and 'email_verification_code' in request.data and 'email' in request.data:
            data = request.data.copy()
            try:
                EmailVerification.objects.get(email=data['email'], verify_code=data['email_verification_code'])
            except EmailVerification.DoesNotExist:
                msg = 'Wrong email verification code'
                return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
            response = code2session(request.data['code'])
            if 'errcode' in response:
                if response['errcode'] == -1:
                    msg = 'System is busy'
                    return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
                elif response['errcode'] == 40029:
                    msg = 'Invalid code'
                    return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
                elif response['errcode'] == 45011:
                    msg = 'Request is too frequent'
                    return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
                elif response['errcode'] == 40013:
                    msg = 'Intern server error, please contact developer'
                    return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
                elif response['errcode'] == 0:
                    return self.do_register(data, response)
                else:
                    return Response(response['errmsg'] + '  original code is ' + request.data['code'],
                                    status=status.HTTP_400_BAD_REQUEST)
            elif 'openid' in response:
                return self.do_register(data, response)
            else:
                msg = 'Unknown error'
                return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
        else:
            msg = 'Missing wx.login code or email address or email_verification_code'
            return JsonResponse({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
