from rest_framework import serializers

from ars.models import ActivityType
from ars.activity.serializers.other_serializers import User_act_Serializer
from ars.activity.serializers.activity_get_serializer import Activity_Get_Serializer


class Activity_Type_Get_Serializer(serializers.ModelSerializer):
    # subscribe_users = UserSerializer(many=True, read_only=True)
    subscribe_users = serializers.SerializerMethodField()
    # type_activities = Activity_Get_Serializer()
    type_activities = serializers.SerializerMethodField()
    

    # type_activities = serializers.PrimaryKeyRelatedField(queryset=ActivityType.objects.all())

    class Meta:
        model = ActivityType
        fields = '__all__'

    def get_type_activities(self, obj):
        # if len(obj.type_activities.all()) == 0:
        #     return {}
        type_activities = obj.type_activities.all()
        type_activities_serializers = Activity_Get_Serializer(instance=type_activities, many=True)
        return type_activities_serializers.data

    def get_subscribe_users(self, obj):
        subscribe_users = obj.subscribe_users.all()
        subscribe_users_serializers = User_act_Serializer(instance=subscribe_users, many=True)
        return subscribe_users_serializers.data

class Activity_Type_Simple_Get_Serializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ActivityType
        fields = ['id', 'name', 'image']

    def get_image(self, obj):
        return obj.image.url if obj.image else ''

class Activity_Type_User_Get_Serializer(serializers.ModelSerializer):
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = ActivityType
        fields = ['id', 'name', 'is_subscribe']
    
    def get_is_subscribe(self, instance):
        user_id = self.context['user_id']
        subscribe_users = instance.subscribe_users.filter(id=user_id)
        if len(subscribe_users) != 0:
            return True
        return False