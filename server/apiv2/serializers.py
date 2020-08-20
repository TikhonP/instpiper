from rest_framework import serializers
from apiv2.models import TokenV2, ProxyV2, RequestV2


class RequestV2CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestV2
        fields = ('user', 'data', 'proxy', 'threads')


    # def create(self, validated_data):
