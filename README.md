> **Warning**: This application is currently in alpha development and is not intended for production use. Use at your own risk as features and APIs may change without notice.

# Cisco Switch Manager

A Django-based application for managing Cisco Catalyst switches.

## Setup on Windows

1. Create and activate virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install requirements:
   ```powershell
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your settings
   ```

4. Initialize database:
   ```powershell
   python manage.py migrate
   ```

5. Create superuser:
   ```powershell
   python manage.py createsuperuser
   ```

6. Run development server:
   ```powershell
   python manage.py runserver
   ```

## Features

- Switch inventory management
  - Add, edit, and delete switch configurations
  - Bulk import switches via CSV
  - Track switch models, IP addresses, and locations
- Configuration management
  - Automated backup of switch configurations
  - Version control for config changes
  - Config comparison tool
- Monitoring and Status
  - Real-time port status monitoring
  - Interface statistics and error tracking
  - VLAN configuration overview
- Security
  - Role-based access control
  - Audit logging of all changes
  - Secure credential storage
- Automation
  - Scheduled configuration backups
  - Automated firmware updates
  - Bulk configuration changes
  - Celery-based task management


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.