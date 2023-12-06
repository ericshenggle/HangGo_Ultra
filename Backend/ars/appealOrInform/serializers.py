from rest_framework import serializers
from ars.models import *
from ars.activity.act_util import MyDateTimeField
from ars.activity.serializers.other_serializers import User_act_Serializer


class Appeal_Serializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    create_time = MyDateTimeField()

    class Meta:
        model = Appeal
        fields = '__all__'

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data


class Inform_Serializer(serializers.ModelSerializer):
    to_user = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    create_time = MyDateTimeField()

    class Meta:
        model = Inform
        fields = '__all__'

    def get_to_user(self, instance):
        user_id = instance.to_user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

    def get_user(self, instance):
        user_id = instance.user_id
        user = User.objects.get(id=user_id)
        serializer = User_act_Serializer(user)
        return serializer.data

