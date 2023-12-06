# 存放了一些工具类
from rest_framework import serializers

APP_ID = 'wx9f6970d0a04d5232'
APP_SECRET = 'cba0da4db779aae76ed914d720edae28'
import requests


def code2session(code):
    response = requests.get(
        f'https://api.weixin.qq.com/sns/jscode2session?appid={APP_ID}&secret={APP_SECRET}&js_code={code}&grant_type=authorization_code')

    return response.json()


def get_access_token():
    response = requests.get(
        f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}'
    )
    response = response.json()
    if 'access_token' in response:
        return response['access_token']
    else:
        return ''


from datetime import datetime


def change_data_time_format(t):
    t = datetime.strptime(
        t,
        "%Y/%m/%d %H:%M"
    )
    return t  # .strftime('%Y-%m-%dT%H:%M')

def change_data_time_format_str(t):
    return t.strftime('%Y/%m/%d %H:%M')
