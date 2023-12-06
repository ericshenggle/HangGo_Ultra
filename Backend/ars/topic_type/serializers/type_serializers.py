from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ars.models import ActivityType, TopicType
from ars.user.serializers import *
from drf_extra_fields.fields import Base64ImageField

class To_Type_Serializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    class Meta:
        model = TopicType
        fields = ['id', 'name', 'image']

    def create(self, validated_data):
        topicType = TopicType.objects.get_or_create(**validated_data)[0]
        return topicType

    def update(self, instance, validated_data):
        # new 
        instance.name = validated_data['name']
        instance.image = validated_data['image'] if 'image' in validated_data.keys() else instance.image
        instance.save()

        #2,返回数据
        topicType = TopicType.objects.get(id=instance.id)
        return topicType

class Topic_Type_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TopicType
        fields = '__all__'

    def validate_name(self, value):
        return value 

    def validate(self, attrs):
        if False:
            raise serializers.ValidationError("类别错误")
        return attrs

    def create(self, validated_data):
        activityType = TopicType.objects.get_or_create(**validated_data)[0]
        return activityType

    # def update(self, instance, validated_data):
    #     # new 
    #     instance.name = validated_data["name"]
    #     instance.save()

    #     #2,返回数据
    #     activityType = ActivityType.objects.get(id=instance.id)
    #     return activityType

'''
class Album(models.Model):
    album_name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)

class Track(models.Model):
    album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
    order = models.IntegerField()
    title = models.CharField(max_length=100)
    duration = models.IntegerField()

    class Meta:
        unique_together = ['album', 'order']
        ordering = ['order']

    def __str__(self):
        return '%d: %s' % (self.order, self.title)

    # def create(self, validated_data):
    #     tracks_data = validated_data.pop('tracks')
    #     album = Album.objects.create(**validated_data)
    #     for track_data in tracks_data:
    #         Track.objects.create(album=album, **track_data)
    #     return album

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        # Unless the application properly enforces that this field is
        # always set, the following could raise a `DoesNotExist`, which
        # would need to be handled.
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.is_premium_member = profile_data.get(
            'is_premium_member',
            profile.is_premium_member
        )
        profile.has_support_contract = profile_data.get(
            'has_support_contract',
            profile.has_support_contract
         )
        profile.save()

        return instance

    def create(self, validated_data):
        """
        根据提供的验证过的数据创建并返回一个新的`Author`实例。
        """
        #将authors 多对多关系的数据从前端传过来的数据中取出，放在authors 中
        authors = validated_data.pop('author')
        #将正常的book的数据进行保存，创建Book实例，并通过book 接收
        book = Book.objects.create(** validated_data)
        #重点中的重点：循环读取authors对象的数据
        for author in authors:
            #实例化author对象
            author = Author.objects.filter(id=author.id).first()
            #将多对多的关系添加到book中
            book.author.add(author)
            #保存book的多对多关系
            book.save()
        return book
'''