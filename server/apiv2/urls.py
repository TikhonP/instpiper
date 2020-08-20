from django.urls import path
from apiv2 import views
from rest_framework import routers

router = routers.SimpleRouter()


urlpatterns = [
    path('requests/request/create/', views.RequestV2CreateView.as_view()),
]
urlpatterns += router.urls
