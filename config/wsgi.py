# config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

# Set the settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Get the WSGI application
application = get_wsgi_application()