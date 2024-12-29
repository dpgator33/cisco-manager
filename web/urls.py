# web/urls.py
from django.urls import path
from . import views
import logging
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

urlpatterns = [
    path('', lambda request: redirect('dashboard'), name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/add/', views.device_add, name='device_add'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),
    path('devices/<int:pk>/delete/', views.device_delete, name='device_delete'),
    path('devices/<int:pk>/test/', views.device_test_connection, name='device_test_connection'),
    path('config/', views.config_list, name='config_list'),
    path('devices/<int:pk>/backup/', views.device_backup_config, name='device_backup_config'),
    path('devices/<int:pk>/refresh/', views.device_refresh_info, name='device_refresh_info'),
    path('devices/<int:pk>/configs/', views.device_configs, name='device_configs'),
    path('devices/<int:pk>/configs/<int:config_id>/', views.device_config_detail, name='device_config_detail'),
    path('configs/search/', views.config_search, name='config_search'),
    path('topology/', views.topology_view, name='topology'),
]

print("Web URLs loaded:", urlpatterns)  # Temporary debug line