from rest_framework import serializers
from ars.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format='%Y/%m/%d %H:%M')
    type = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'content', 'not_type', 'created_time', 'isread', 'type', 'data', 'user']

    def get_type(self, instance):
        if instance.type == Notification.Type.活动:
            return "活动"
        elif instance.type == Notification.Type.委托:
            return "委托"
        elif instance.type == Notification.Type.话题:
            return "话题"
        else:
            return

    def get_data(self, instance):
        if instance.type == Notification.Type.活动:
            return instance.activity.id
        elif instance.type == Notification.Type.委托:
            return instance.commission.id
        elif instance.type == Notification.Type.话题:
            return instance.topic.id
        else:
            return
