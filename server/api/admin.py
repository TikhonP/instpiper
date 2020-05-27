from django.contrib import admin
from .models import Token, Req, Proxy


admin.site.register(Token)
admin.site.register(Req)
admin.site.register(Proxy)
