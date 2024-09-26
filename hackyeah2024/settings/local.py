from .base import *

SECRET_KEY = "secret_key"

# ------------- DATABASES -------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "hackyeah2024"),
        "USER": env("POSTGRES_USER", "hackyeah2024"),
        "PASSWORD": env("POSTGRES_PASSWORD", "hackyeah2024"),
        "HOST": env("POSTGRES_HOST", "localhost"),
    }
}
