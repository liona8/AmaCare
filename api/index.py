import sys
import os

# Add the amacare directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'amacare'))

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'amacare.settings'

import django
django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
