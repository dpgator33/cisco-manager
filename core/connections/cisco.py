# core/connections/cisco.py
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, AuthenticationException
from typing import Dict, Any, Optional

class CiscoConnection:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        enable_password: Optional[str] = None,
        device_type: str = 'cisco_ios'
    ):
        self.device_params = {
            'device_type': device_type,
            'host': host,
            'username': username,
            'password': password,
            'secret': enable_password if enable_password else password,
            'global_delay_factor': 2,
            'port': 22,
            'global_cmd_verify': False,
            'use_keys': False,
            'allow_agent': False,
        }
        self._connection = None

    def connect(self):
        """Establish connection to device."""
        if not self._connection:
            self._connection = ConnectHandler(**self.device_params)
            self._connection.enable()
        return self._connection

    def close(self):
        """Close the connection if it exists."""
        if self._connection:
            self._connection.disconnect()
            self._connection = None

    def test_connection(self) -> Dict[str, Any]:
        """Test SSH connection to device and gather basic information."""
        try:
            print(f"Attempting to connect to {self.device_params['host']}")
            connection = self.connect()
            
            # Get the hostname from the prompt
            hostname = connection.find_prompt()
            print(f"Found hostname: {hostname}")
            
            # Try to get version info
            print("Getting version info...")
            version_output = connection.send_command('show version')
            print(f"Version output received: {version_output[:200]}...")  # Print first 200 chars
            
            # Try to get basic interface status
            print("Getting interface status...")
            interface_output = connection.send_command('show ip interface brief')
            print(f"Interface output received: {interface_output[:200]}...")
            
            return {
                'status': 'success',
                'message': f'Successfully connected to {hostname}',
                'hostname': hostname,
                'version': version_output,
                'interfaces': interface_output
            }
        except NetMikoTimeoutException as e:
            print(f"Timeout error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Timeout connecting to {self.device_params["host"]}: {str(e)}'
            }
        except AuthenticationException as e:
            print(f"Authentication error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Authentication failed for {self.device_params["host"]}: {str(e)}'
            }
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error connecting to {self.device_params["host"]}: {str(e)}'
            }
        finally:
            self.close()

    def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information."""
        try:
            connection = self.connect()
            
            # Get version information
            version_output = connection.send_command('show version')
            
            # Get hostname
            hostname = connection.find_prompt().rstrip('#')
            
            # Get basic interface status
            interfaces_output = connection.send_command('show ip interface brief')
            
            # Get memory usage
            memory_output = connection.send_command('show memory statistics')
            
            # Get CPU usage
            cpu_output = connection.send_command('show processes cpu | include CPU utilization')
            
            return {
                'status': 'success',
                'hostname': hostname,
                'interfaces': interfaces_output,
                'version_info': version_output,
                'memory_info': memory_output,
                'cpu_info': cpu_output
            }
            
        except (NetMikoTimeoutException, AuthenticationException) as e:
            return {
                'status': 'error',
                'message': f"Connection failed: {str(e)}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error getting device info: {str(e)}"
            }
        finally:
            self.close()

    def get_running_config(self) -> str:
        """Get the running configuration from the device."""
        try:
            connection = self.connect()
            
            # Send terminal length 0 to disable pagination
            connection.send_command('terminal length 0')
            
            # Get running config
            config = connection.send_command('show running-config')
            
            return config
            
        except Exception as e:
            raise Exception(f"Failed to get running configuration: {str(e)}")
        finally:
            self.close()