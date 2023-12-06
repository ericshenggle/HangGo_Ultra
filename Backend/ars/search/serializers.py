from rest_framework import serializers
from ars.models import *


class Keyword_Serializer(serializers.ModelSerializer):
    # search_time = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    class Meta:
        model = Keyword
        fields = ['id', 'keyword', 'search_time']
