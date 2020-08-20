from rest_framework import generics
from apiv2.serializers import RequestV2CreateSerializer


class RequestV2CreateView(generics.CreateAPIView):
    serializer_class = RequestV2CreateSerializer
