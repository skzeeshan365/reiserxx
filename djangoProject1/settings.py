import os.path
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv('.env')

CLOUD_NAME = os.getenv('CLOUD_NAME')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

INFERENCE_API = os.getenv('INFERENCE_API')
VOCALHOST_API = os.getenv('VOCALHOST_API')

SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '13.233.151.164', 'localhost', 'reiserx.com']

# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reiserx.apps.ReiserxConfig',
    'administration.apps.AdministrationConfig',
    'main.apps.MainConfig',
    'cloudinary_storage',
    'cloudinary',
    'tinymce',
    'django.contrib.sitemaps',
    'captcha',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUD_NAME,
    'API_KEY': API_KEY,
    'API_SECRET': API_SECRET,
    'FOLDER': 'reiserx'
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

ROOT_URLCONF = 'djangoProject1.urls'

ASSET_VERSION = 'v2'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'djangoProject1.context_processors.asset_version'
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoProject1.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

NAME = os.getenv('DB_NAME')
HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
PORT = os.getenv('DB_PORT')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': NAME,
        'HOST': HOST,
        'USER': USER,
        'PASSWORD': PASSWORD,
        'PORT': PORT,
        'OPTIONS': {
            'ssl': {
                'ca': 'djangoProject1/DigiCertGlobalRootCA.crt.pem',
            }
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

FILER_ENABLE_PERMISSIONS = True
FILER_FILE_STORAGE_BACKEND = 'django_cloudinary.storage.MediaCloudinaryStorage'

TINYMCE_DEFAULT_CONFIG = {
    'plugins': 'image, code',
    'toolbar': 'undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | code',
    'width': '100%',
    'height': 300,
    'image_upload_url': '/tinymce_upload/',  # use your desired upload URL
    'imageupload_enabled': True,
}

RECAPTCHA_PUBLIC_KEY = os.getenv('CAPTCHA_SITE_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('CAPTCHA_SITE_SECRET_KEY')

BASE_URL = 'https://www.reiserx.com'

DEFAULT_FROM_EMAIL = "skzeeshan3650@gmail.com"
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
VERIFALIA_USERNAME = os.getenv('VERIFALIA_USERNAME')
VERIFALIA_PASSWORD = os.getenv('VERIFALIA_PASSWORD')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '{asctime} {levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'django.log',
                'formatter': 'standard',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
            },
            'django.request': {
                'handlers': ['file'],
                'level': 'ERROR',
            },
        },
    }


WHITENOISE_USE_FINDERS = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
