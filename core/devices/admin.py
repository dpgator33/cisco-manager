# core/devices/admin.py
from django.contrib import admin
from .models import Device

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'device_type', 'status', 'last_checked']
    list_filter = ['status', 'device_type']
    search_fields = ['name', 'ip_address']
    ordering = ['name']