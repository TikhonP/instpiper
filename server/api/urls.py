from django.urls import path
from . import views


urlpatterns = [
    path('createrequest', views.CreateRecRequest, name='CreateRequest'),
    path('private', views.privateapi, name='private'),
    path('checkrequest', views.CheckComplite, name='CheckComplite'),
    path('getdata', views.GetData, name='GetData'),
]
 
