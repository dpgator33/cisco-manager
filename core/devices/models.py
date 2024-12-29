# core/devices/models.py
from django.db import models
from django.core.validators import validate_ipv4_address

class Device(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.CharField(
        max_length=15,
        validators=[validate_ipv4_address]
    )
    device_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='inactive'
    )
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    enable_password = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    last_checked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    class Meta:
        ordering = ['name']

class Configuration(models.Model):
    device = models.ForeignKey('Device', on_delete=models.CASCADE, related_name='configurations')
    timestamp = models.DateTimeField(auto_now_add=True)
    config_type = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running Config'),
            ('startup', 'Startup Config'),
        ],
        default='running'
    )
    content = models.TextField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name} - {self.config_type} - {self.timestamp}"