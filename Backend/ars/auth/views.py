from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ars.utils import code2session

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers, status


class WxAuthSerializerClass(serializers.Serializer):
    code = serializers.CharField(
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        code = attrs.get('code')

        if code is not None:
            response = code2session(code)
            if 'errcode' in response:
                if response['errcode'] == -1:
                    msg = _('System is busy, please try again later')
                    raise serializers.ValidationError(msg, code='authorization')
                elif response['errcode'] == 40029:
                    msg = _('Invalid code')
                    raise serializers.ValidationError(msg, code='authorization')
                elif response['errcode'] == 45011:
                    msg = _('Request is too frequent')
                    raise serializers.ValidationError(msg, code='authorization')
                elif response['errcode'] == 40013:
                    msg = _('Intern server error, please contact developer')
                    raise serializers.ValidationError(msg, code='authorization')
                elif response['errcode'] == 0:
                    user = authenticate(request=None, response=response)
                    if not user:
                        msg = _('User does not exists')
                        raise serializers.ValidationError(msg, code='authorization')
            if 'openid' in response:
                user = authenticate(request=None, response=response)
                if not user:
                    msg = _('User does not exists')
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = _('Unknown error')
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = _('Missing Authorization code')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class WxAuthToken(ObtainAuthToken):
    serializer_class = WxAuthSerializerClass

    @swagger_auto_schema(
        operation_summary='已经注册的用户的登录',
        operation_description='传入的参数只需要带有wx.login得到的code。如果该用户确实已经注册，则返回http status=200，返回token,user_id和email。其中token作为后续的用户身份确认方式，放置在http header中，字段名称为Authorization，后面的格式为字符串\'token 获取到的token\'。' +
                              '如果该用户没有注册或者code无效，返回状态码http status=400 (bad request)',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": openapi.Schema(type=openapi.TYPE_STRING, description='wx.login()得到的code')
            },
        ),
        responses={200: '成功 其中{token:String, user_id: integer, email: String}', 400: '非法用户ID'}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({
                'errcode': 1,
                'user_id': user.pk,
                'email': user.email
            })
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'errcode': 0,
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


openid_email = openapi.Parameter('email', in_=openapi.IN_QUERY, description='email',
                                 type=openapi.TYPE_STRING)
openid_password = openapi.Parameter('password', in_=openapi.IN_QUERY, description='password',
                                    type=openapi.TYPE_STRING)


class WebLogin(ObtainAuthToken):

    @swagger_auto_schema(
        operation_summary='Web登录（账号+密码）',
        operation_description='如果登录失败，message字段说明失败原因，如果成功，token字段中有后续使用的token',
        responses={200: '登录成功', 400: '缺少账号或密码', 401: '账号或密码错误，用户未激活或者用户不是管理员'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='password')
            },
        ),
    )
    def post(self, request):
        user = authenticate(request=request)
        if user is not None and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_200_OK)
        if user is not None and user.is_active == False:
            return Response({
                'message': '用户未激活或用户不是管理员'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'message': '账号或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
