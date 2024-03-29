from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('', include('home.urls')),
    path('pages/', include('pages.urls')),
    path('tools/', include('manage_db_tools.urls')),
    path('api/v2/', include('apiv2.urls')),
]
