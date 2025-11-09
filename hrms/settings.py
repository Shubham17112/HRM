from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#@)7skdk^es777@bv^pyjm1f2x-)71-t0sblhavtn8s%hc=@r9'

DEBUG = True
ALLOWED_HOSTS = [
      'overgrateful-luniest-felisa.ngrok-free.dev',
         'localhost',
    '127.0.0.1',
      ".ngrok-free.app",
    ".ngrok-free.dev",
]

# -------------------
# Installed Apps
# -------------------
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
   
 # or allow ngrok wildcard domains:
  
    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    'accounts',
    'company',
    'self_signup',
    'employee_portal',
    'payments',
      'widget_tweaks',
]
# settings.py
CSRF_TRUSTED_ORIGINS = [
    "https://overgrateful-luniest-felisa.ngrok-free.dev",
    "https://*.ngrok-free.app",   # allow wildcard for convenience
    "https://*.ngrok-free.dev",
]
# settings.py
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# settings.py

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SITE_ID = 1

# -------------------
# Authentication Backends
# -------------------
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
     'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    # 'allauth.account.auth_backends.AuthenticationBackend',  # Allauth auth
]

# -------------------
# Allauth Settings
# -------------------
# ACCOUNT_AUTHENTICATION_METHOD = 'username'   # or 'email' or 'username_email'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'optional' or 'mandatory' if needed


ACCOUNT_LOGIN_METHODS = {"username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/post_login_redirect/'
LOGOUT_REDIRECT_URL = '/'

# -------------------
# Email Settings
# -------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'personal17122004@gmail.com'
EMAIL_HOST_PASSWORD = 'nshekvfidvuautlw'

# -------------------
# Middleware
# -------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'hrms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hrms.wsgi.application'

# -------------------
# Database
# -------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------
# Password Validation
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# -------------------
# Internationalization
# -------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------
# Static Files
# -------------------
STATIC_URL = 'static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']

# -------------------
# Default Primary Key
# -------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


RAZORPAY_KEY_ID = "rzp_test_RRhqTWeNC1il5O"
RAZORPAY_KEY_SECRET = "jMmnfPNl1hkXpLc7SHtJWjO0"
INSTALLED_APPS += ['django_extensions']
