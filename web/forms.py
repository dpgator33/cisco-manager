from django import forms
from core.devices.models import Device

class DeviceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    enable_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank if same as password'
    )
    
    class Meta:
        model = Device
        fields = ['name', 'ip_address', 'device_type', 'location', 'username', 'password', 'enable_password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }