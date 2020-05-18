from django.urls import path
from . import views


urlpatterns = [
    path('createrequest/', views.CreateRecRequest, name='CreateRequest'),
]
 
