'''
from rest_framework import serializers

from ars.models import LectureInfo


class Lecture_Serializer(serializers.ModelSerializer):
    #activity = Activity_Serializer()

    class Meta:
        model = LectureInfo
        fields = '__all__'
        read_only_fields = ['activity']

    # def create(self, validated_data):
    #     activity_data = validated_data.pop('activity')
    #     re_activity = Activity_Serializer(data=activity_data)
    #     activityInfo = LectureInfo.objects.create(
    #         activity = re_activity,
    #         **validated_data
    #     )

    def update(self, instance, validated_data):
        #activity_data = validated_data.pop('activity')
        #re_activity = instance.activity

        #act = Activity_Serializer(instance=re_activity, data=activity_data)
        #if act.is_valid():
        #    act.save()
        instance.week = validated_data['week']
        instance.start_class = validated_data['start_class']
        instance.end_class = validated_data['end_class']
        instance.save()
        # for key, value in validate_data.items():
        #     setattr(instance, key, value)
        # instance.save()
        return instance
'''