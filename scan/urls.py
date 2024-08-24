from django.urls import path
from . import views

urlpatterns = [
    path('initiate_scan/', views.initiate_scan, name='initiate_scan'),
    path('scan_results/', views.scan_results, name='scan_results'),
    path('scan_results/<int:scan_id>/', views.scan_results, name='scan_results_with_id'),
]
