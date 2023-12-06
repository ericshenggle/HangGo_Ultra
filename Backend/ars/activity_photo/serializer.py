from rest_framework import serializers
from ars.models import ActivityPhoto


class ActivityPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPhoto
        fields = '__all__'
