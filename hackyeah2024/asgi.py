import os

from django.core.wsgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "hackyeah2024.settings.production"
)

application = get_asgi_application()
