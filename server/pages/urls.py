from django.urls import path
from . import views


urlpatterns = [
    path('privacy/', views.privacy, name='privacy'),
    path('docs/api/', views.docs_api, name='docs_api'),
]
