from rest_framework import serializers
from ars.models import *


class Commission_SearchRecord_Serializer(serializers.ModelSerializer):
    # search_time = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    class Meta:
        model = SearchRecord_Commission
        fields = ['id', 'keyword', 'search_time']
