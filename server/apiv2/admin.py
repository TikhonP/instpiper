from django.contrib import admin
from .models import TokenV2, RequestV2, ProxyV2


admin.site.register(TokenV2)
admin.site.register(RequestV2)
admin.site.register(ProxyV2)
