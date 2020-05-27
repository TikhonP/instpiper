from django.urls import path
from . import views


urlpatterns = [
    path('addtoken/', views.addtoken, name='addtoken'),
    path('removetoken/', views.removetoken, name='removetoken'),
    path('removereq/', views.removerequest, name='removerequest'),
    path('removeproxy/', views.removeproxy, name='removeproxy'),
    path('renameproxy/', views.renameproxy, name='renameproxy'),
    path('addproxy/', views.addproxy, name='addproxy'),
    path('downloadcsv/', views.dounload_csv_output, name='download_output_csv'),
]
