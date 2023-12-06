# -*- coding: utf-8 -*-
import os
import sys
import django
from django.http import HttpResponse

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buaase.settings')

django.setup()

from ars.models import *
from ars.activity.views.activity_views import Activity_All_View


def create_type():
    act_types = ['体育', '课程', '文艺', '表演', '讲座', '聚会', '游戏', '比赛', '博雅']
    t = {"name": 1}
    for i in act_types:
        t["name"] = i
        ActivityType.objects.get_or_create(**t)


def create_user():
    u = {
        "username": "ycg12",
        "nickName": "ycg12",
        "avatarUrl": "string",
        "email": "user@example.com",
        "openid": "12345",
        "age": 0,
        "gender": 0,
        "student_id": "1111112",
        "phone": "111112",
        'audit_status': 2
    }
    User.objects.get_or_create(**u)


def create_normal_activity():
    id = User.objects.get(username='ycg').id
    l_1 = {
        "start_at": "2021/05/2 8:00",
        "end_at": "2021/05/3 11:55",
        "description": "this is a sports",
        "allow_total": 211,
        "activity": {
            "name": "act_1",
            "activity_type": {"name": "体育"},
            "start_enrollment_at": "2021/04/26 8:00",
            "end_enrollment_at": "2021/05/26 8:00",
            "create_user": id,
            "location": 1,
            "position": "adddd",
            "public_status": 1,
            "audit_status": 1,
            "tags": [
                {
                    "name": "篮球"
                },
                {
                    "name": "运动"
                }
            ]
        }
    }
    l_2 = {
        "start_at": "2021/05/7 8:00",
        "end_at": "2021/05/9 11:55",
        "description": "this is a per",
        "allow_total": 321,
        "activity": {
            "name": "act_2",
            "activity_type": {"name": "文艺"},
            "start_enrollment_at": "2021/04/26 8:00",
            "end_enrollment_at": "2021/05/26 8:00",
            "create_user": id,
            "location": 2,
            "position": "wei",
            "public_status": 1,
            "audit_status": 1,
            "tags": [
                {
                    "name": "晨星"
                },
                {
                    "name": "博雅"
                }
            ]
        }
    }

    class A:
        def __init__(self):
            self.data = None
            self.user = None
            self.FILES = {}

    view = Activity_All_View()
    request = A()
    request.data = l_1
    request.user = User.objects.get(username='ycg')
    view.post(request)
    request.data = l_2
    view.post(request)


def create_lecture():
    id = User.objects.get(username='ycg').id
    l_1 = {
        "week": 12,
        "start_class": 3,
        "end_class": 5,
        "activity": {
            "name": "act_3",
            "activity_type": {"name": "课程"},
            "start_enrollment_at": "2021/04/26 8:00",
            "end_enrollment_at": "2021/05/26 8:00",
            "create_user": id,
            "location": 1,
            "position": "adddd",
            "public_status": 1,
            "audit_status": 1,
            "tags": [
                {
                    "name": "数学"
                },
                {
                    "name": "高代"
                }
            ]
        }
    }
    l_2 = {
        "week": 12,
        "start_class": 3,
        "end_class": 5,
        "activity": {
            "name": "act_4",
            "activity_type": {"name": "课程"},
            "start_enrollment_at": "2021/04/26 8:00",
            "end_enrollment_at": "2021/05/26 8:00",
            "create_user": id,
            "location": 2,
            "position": "wei",
            "public_status": 1,
            "audit_status": 1,
            "tags": [
                {
                    "name": "数学"
                },
                {
                    "name": "微积分"
                }
            ]
        }
    }

    class A:
        def __init__(self):
            self.data = None
            self.user = None
            self.FILES = {}

    view = Activity_All_View()
    request = A()
    request.data = l_1
    request.user = User.objects.get(username='ycg')
    view.post(request)
    request.data = l_2
    view.post(request)


def create_activity():
    create_normal_activity()
    create_lecture()


def init_db():
    # import pdb; pdb.set_trace()
    # create_user()
    # create_type()
    create_activity()
    return HttpResponse()


if __name__ == '__main__':
    init_db()
    print("Done!")
