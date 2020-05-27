from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.loginp, name='loginp'),
    path('register/', views.registerp, name='registerp'),
    path('logout/', views.logoutp, name='logout'),
    path('makerequest/', views.makerequest, name='makerequest'),
]
