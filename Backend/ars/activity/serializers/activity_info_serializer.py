from rest_framework import serializers

from ars.models import *
from ars.activity.act_util import *

class ActivityInfo_Serializer(serializers.ModelSerializer):
    start_at = MyDateTimeField()
    end_at = MyDateTimeField()

    class Meta:
        model = ActivityInfo
        fields = [
            'start_at', 'end_at', 'description', 'allow_total'
        ]
        read_only_fields = ['activity']

    # nested 需要重写
    '''
    def create(self, validated_data):
        import pdb; pdb.set_trace()
        
        activity_data = dict(validated_data.pop('activity'))
        re_activity = Activity_Serializer(data=activity_data)
        if re_activity.is_valid(raise_exception=True):
            re_activity.save()
            re_activity = re_activity.data
        activityInfo = ActivityInfo.objects.create(
            activity = re_activity,
            **validated_data
        )
        return activityInfo
    '''

    def update(self, instance, validated_data):
        instance.start_at = validated_data['start_at']
        instance.end_at = validated_data['end_at']
        instance.description = validated_data['description']
        instance.allow_total = validated_data['allow_total']
        instance.save()

        return instance
