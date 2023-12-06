from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ars.models import Activity, ActivityType, Tag

class Tag_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    def validate_name(self, value):
        return value 

    def validate(self, attrs):
        if False:
            raise serializers.ValidationError("类别错误")
        return attrs

    def create(self, validated_data):
        tag = Tag.objects.get_or_create(
            name = validated_data['name'],
        )[0]
        return tag

    # def update(self, instance, validated_data):
    #     # new 
    #     instance.name = validated_data["name"]
    #     instance.save()

    #     #2,返回数据
    #     tag = Tag.objects.get(id=instance.id)
    #     return tag


