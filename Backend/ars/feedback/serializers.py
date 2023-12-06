from rest_framework import serializers
from ars.models import FeedBack
from ars.user.serializers import UserSerializer


class FeedBackSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = FeedBack
        fields = '__all__'
        depth = 1
