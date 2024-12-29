# web/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DeviceForm
from core.devices.models import Device, Configuration
from core.connections.cisco import CiscoConnection
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone

@login_required
def dashboard(request):
    """View for the main dashboard."""
    # Get device counts
    devices = Device.objects.all()
    total_devices = devices.count()
    active_devices = devices.filter(status='active').count()
    attention_needed = devices.exclude(status='active').count()
    
    # Get recent devices
    recent_devices = devices.order_by('-last_checked')[:5]
    
    return render(request, 'dashboard/index.html', {
        'total_devices': total_devices,
        'active_devices': active_devices,
        'attention_needed': attention_needed,
        'recent_devices': recent_devices,
    })

@login_required
def device_list(request):
    """View for listing all devices."""
    devices = Device.objects.all().order_by('name')
    return render(request, 'devices/list.html', {'devices': devices})

@login_required
def device_add(request):
    """View for adding a new device."""
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            if 'test_connection' in request.POST:
                # Test connection only
                connection = CiscoConnection(
                    host=form.cleaned_data['ip_address'],
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    enable_password=form.cleaned_data['enable_password']
                )
                result = connection.test_connection()
                
                if result['status'] == 'success':
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
                    
                return render(request, 'devices/add.html', {'form': form})
            else:
                # Save the device
                device = form.save(commit=False)
                device.status = 'inactive'  # Default status
                device.save()
                messages.success(request, f'Device {device.name} has been added successfully.')
                return redirect('device_list')
    else:
        form = DeviceForm()
    
    return render(request, 'devices/add.html', {'form': form})

# web/views.py

@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    
    # Get initial context
    context = {
        'device': device,
        'device_info': None
    }
    
    # If requested, poll device for real-time info
    if request.GET.get('refresh') == 'true':
        connection = CiscoConnection(
            host=device.ip_address,
            username=device.username,
            password=device.password,
            enable_password=device.enable_password
        )
        device_info = connection.get_device_info()
        
        if device_info['status'] == 'success':
            context['device_info'] = device_info
            # Update device status
            device.status = 'active'
            device.last_checked = timezone.now()
            device.save()
        else:
            device.status = 'error'
            device.save()
            messages.error(request, f"Error getting device info: {device_info.get('message')}")
    
    return render(request, 'devices/detail.html', context)

@login_required
def config_list(request):
    """View for listing device configurations."""
    configs = Configuration.objects.select_related('device').order_by('-timestamp')
    return render(request, 'config/list.html', {
        'configs': configs
    })

@login_required
@require_POST
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    device_name = device.name
    device.delete()
    messages.success(request, f'Device {device_name} has been deleted.')
    return redirect('device_list')


@login_required
@require_POST
def device_test_connection(request, pk):
    device = get_object_or_404(Device, pk=pk)
    print(f"\nTesting connection to device: {device.name} ({device.ip_address})")
    
    try:
        connection = CiscoConnection(
            host=device.ip_address,
            username=device.username,
            password=device.password,
            enable_password=device.enable_password
        )
        
        result = connection.test_connection()
        print(f"\nConnection test result: {result['status']}")
        
        if result['status'] == 'success':
            device.status = 'active'
            device.last_checked = timezone.now()
            device.save()
            
            # Store additional information in the response
            return JsonResponse({
                'status': 'success',
                'message': result['message'],
                'details': {
                    'hostname': result.get('hostname', 'Unknown'),
                    'version_info': result.get('version', 'Not available'),
                    'interface_info': result.get('interfaces', 'Not available')
                }
            })
        else:
            device.status = 'error'
            device.save()
            return JsonResponse(result)
            
    except Exception as e:
        error_msg = f"Error testing connection: {str(e)}"
        print(f"\nError: {error_msg}")
        device.status = 'error'
        device.save()
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        })

@login_required
@require_POST
def device_backup_config(request, pk):
    print(f"\nBackup request received for device: {pk}")
    device = get_object_or_404(Device, pk=pk)
    
    connection = CiscoConnection(
        host=device.ip_address,
        username=device.username,
        password=device.password,
        enable_password=device.enable_password
    )
    
    try:
        # Add more detailed logging
        print("Starting backup process...")
        connection_result = connection.test_connection()
        if connection_result['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'Could not connect to device'
            })
        
        # Get running config
        print("Getting running config...")
        config_content = connection.get_running_config()
        print(f"Config content length: {len(config_content) if config_content else 0}")
        
        # Save configuration
        print("Saving configuration to database...")
        config = Configuration.objects.create(
            device=device,
            config_type='running',
            content=config_content
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Configuration backed up successfully',
            'config': {
                'id': config.id,
                'timestamp': config.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'type': config.config_type
            }
        })
        
    except Exception as e:
        print(f"Error in backup process: {str(e)}")  # Add this line
        return JsonResponse({
            'status': 'error',
            'message': f'Error backing up configuration: {str(e)}'
        })
    finally:
        connection.close()

@login_required
@require_POST
def device_refresh_info(request, pk):
    """AJAX endpoint to refresh device information."""
    device = get_object_or_404(Device, pk=pk)
    
    connection = CiscoConnection(
        host=device.ip_address,
        username=device.username,
        password=device.password,
        enable_password=device.enable_password
    )
    
    device_info = connection.get_device_info()
    
    if device_info['status'] == 'success':
        device.status = 'active'
        device.last_checked = timezone.now()
        device.save()
        return JsonResponse(device_info)
    else:
        device.status = 'error'
        device.save()
        return JsonResponse({
            'status': 'error',
            'message': device_info.get('message', 'Failed to get device information')
        })

@login_required
def device_configs(request, pk):
    device = get_object_or_404(Device, pk=pk)
    configs = Configuration.objects.filter(device=device).order_by('-timestamp')
    return JsonResponse({
        'configs': [{
            'id': config.id,
            'type': config.config_type,
            'timestamp': config.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for config in configs]
    })

@login_required
def device_config_detail(request, pk, config_id):
    device = get_object_or_404(Device, pk=pk)
    config = get_object_or_404(Configuration, pk=config_id, device=device)
    return JsonResponse({
        'content': config.content,
        'timestamp': config.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'type': config.config_type
    })

@login_required
def config_search(request):
    query = request.GET.get('q', '')
    if query:
        configs = Configuration.objects.filter(
            content__icontains=query
        ).select_related('device').order_by('-timestamp')[:50]
        
        results = []
        for config in configs:
            # Find all instances of the query in the content
            content_lower = config.content.lower()
            query_lower = query.lower()
            start_pos = 0
            while True:
                pos = content_lower.find(query_lower, start_pos)
                if pos == -1:  # No more instances found
                    break
                    
                # Extract snippet around this instance
                snippet_start = max(0, pos - 50)
                snippet_end = min(len(config.content), pos + len(query) + 150)
                snippet = config.content[snippet_start:snippet_end]
                
                # Add ellipsis if we're not at the start/end
                if snippet_start > 0:
                    snippet = '...' + snippet
                if snippet_end < len(config.content):
                    snippet = snippet + '...'
                
                results.append({
                    'device_name': config.device.name,
                    'device_id': config.device.id,
                    'config_id': config.id,
                    'timestamp': config.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': config.config_type,
                    'snippet': snippet,
                    'match_position': pos  # Include position for reference
                })
                
                start_pos = pos + 1  # Move past this instance
        
        # Sort results by timestamp (newest first) and then by match position
        results.sort(key=lambda x: (-int(x['timestamp'].replace('-','').replace(' ','').replace(':','')), 
                                  x['match_position']))
        
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

@login_required
def topology_view(request):
    """View for network topology visualization."""
    devices = Device.objects.all().order_by('name')
    return render(request, 'topology/index.html', {
        'devices': devices,
    })