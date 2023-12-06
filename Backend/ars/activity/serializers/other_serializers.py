from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ars.models import *
from ars.activity_tag.serializers import *

import pytz
time_format = "%Y/%m/%d %H:%M"

class User_act_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickName', 'avatarUrl', 'email', 'age', 'gender', 'audit_status',
                  'is_staff']
        read_only_fields = ['id', 'audit_status', 'is_staff']