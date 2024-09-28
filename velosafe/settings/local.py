from .base import *

SECRET_KEY = "secret_key"

# ------------- DATABASES -------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "velosafe"),
        "USER": env("POSTGRES_USER", "velosafe"),
        "PASSWORD": env("POSTGRES_PASSWORD", "velosafe"),
        "HOST": env("POSTGRES_HOST", "localhost"),
    }
}
