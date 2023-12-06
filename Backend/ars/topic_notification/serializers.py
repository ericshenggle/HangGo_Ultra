from rest_framework import serializers
from ars.models import Topic_Notification


class Topic_NotificationSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    class Meta:
        model = Topic_Notification
        fields = ['id', 'content', 'type', 'created_time', 'isread', 'topic', 'user']
