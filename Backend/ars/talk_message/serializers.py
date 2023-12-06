from rest_framework import serializers

from ars.models import TalkMessage
from ars.user.serializers import UserPublicSerializer


class TalkMessageSerializer(serializers.ModelSerializer):
    from_user = UserPublicSerializer(many=False)
    created_time = serializers.DateTimeField(format='%Y/%m/%d %H:%M:%S')

    class Meta:
        model = TalkMessage
        fields = ['id', 'content', 'from_user', 'is_read', 'created_time']
        depth = 1
