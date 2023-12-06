from django.contrib.auth.models import User, Group
from rest_framework import serializers

from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer
from ars.models import Activity, Tag

from ars.activity.serializers.activity_serializers import *

class Tag_Get_Serializer(serializers.ModelSerializer):
    # tag_activities = Activity_Get_Serializer(many=True)
    tag_activities = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = '__all__'    

    def get_tag_activities(self, obj):
        # if len(obj.type_activities.all()) == 0:
        #     return {}
        tag_activities = obj.tag_activities.all()
        tag_activities_serializers = Activity_Get_Serializer(instance=tag_activities, many=True)
        return tag_activities_serializers.data

class Tag_Simple_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']    