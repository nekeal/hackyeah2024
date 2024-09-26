from .base import *

DEBUG = False
SECRET_KEY = "secret_key"

# ------------- LOGGING -------------
LOGGING = {}

# ------------- MIDDLEWARES -------------
MIDDLEWARE = list(filter(lambda x: "DebugToolbarMiddleware" not in x, MIDDLEWARE))

# ------------- PASSWORDS -------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

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
