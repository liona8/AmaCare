import sys
import os
from pathlib import Path

# Get the absolute path to the amacare directory
BASE_DIR = Path(__file__).resolve().parent.parent
AMACARE_DIR = BASE_DIR / 'amacare'

# Add amacare directory to Python path so Django can find 'amacare.settings'
sys.path.insert(0, str(AMACARE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amacare.settings')

# Setup Django
import django
django.setup()

# Get WSGI application
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

# Vercel requires the application to be named 'app'
async def handler(request):
    """Handle incoming HTTP requests"""
    # Convert Vercel request to WSGI environ
    from werkzeug.wrappers import Request, Response
    environ = {
        'REQUEST_METHOD': request['method'],
        'SCRIPT_NAME': '',
        'PATH_INFO': request['path'],
        'QUERY_STRING': request.get('querystring', ''),
        'CONTENT_TYPE': request['headers'].get('content-type', ''),
        'CONTENT_LENGTH': request['headers'].get('content-length', ''),
        'SERVER_NAME': request['headers'].get('host', 'localhost').split(':')[0],
        'SERVER_PORT': request['headers'].get('host', 'localhost').split(':')[1] if ':' in request['headers'].get('host', '') else '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.get('body', b''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add headers to environ
    for key, value in request['headers'].items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value
    
    # Call WSGI app
    response_status = None
    response_headers = []
    
    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers
    
    response_data = app(environ, start_response)
    
    # Build response
    body = b''.join(response_data)
    status_code = int(response_status.split(' ')[0])
    
    headers = {key.lower(): value for key, value in response_headers}
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body.decode('utf-8', errors='replace') if isinstance(body, bytes) else body
    }
