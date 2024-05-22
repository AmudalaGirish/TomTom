import os
from pathlib import Path
# import environ
from decouple import config
# env = environ.Env()
# environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-u@d7t7-xo!9-#@j7i815@q-+3$yvtd)z&yzv!cx=yap22t1pc!'
DEBUG = True

# TOM_API_KEY = env('API_KEY')

ALLOWED_HOSTS = ["*", "192.168.25.242"]


INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'maps',
    "push_notifications",
    'webpush',
    'notifications',
    'paypal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tomtom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'maps', 'templates'),
                 os.path.join(BASE_DIR, 'chat', 'templates'),
                 os.path.join(BASE_DIR, 'paypal', 'templates'),

                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
ASGI_APPLICATION = 'tomtom.asgi.application'
WSGI_APPLICATION = 'tomtom.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


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

# WEBPUSH_SETTINGS = {
#     "VAPID_PUBLIC_KEY": "BBLpa4tFlajDEvCgX_HMIftK55C6vq-coMvNnIlnOPnXvkCDRdNRQrqqcWWo4K8pZpwlChSgF8GkmpJrJrqLjE0",
#     "VAPID_PRIVATE_KEY":"XYG1ZvV4IgotAp_--iR7wfxhJSF4G_hUdOd7MvonHQc",
#     "VAPID_ADMIN_EMAIL": "girishamudala91@gmail.com"
# }

PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": "AIzaSyDkSVsVdByEFIqQiMgEPvHq5DQPJGFLgO0",
    "FCM_PROJECT_ID": "travel-master-97715",
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'maps', 'static'),
    os.path.join(BASE_DIR, 'paypal', 'static'),
]

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ...


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ReportLab A4 Size of PDF
PAGE_SIZE = (595.275, 841.89)

VAPID_PUBLIC_KEY = "BASurhxWN80cYcss_4_EPPmtyvuBN82PuqFsFM-uhvpdjifkowH5Qwos4I1UIe_-tdR3zuCEqmiGkGcn5FqmXxI"
VAPID_PRIVATE_KEY = "YVrf5aCDEZTfeKMkh0fJd2TFY3wTSiJ4CG4khfJSHOs"
VAPID_EMAIL = "mailto:girishamudala91@gmail.com"


WP_PRIVATE_KEY = 'tomtom/private_key.pem'
WP_PUBLIC_KEY = 'tomtom/public_key.pem'

LOGIN_REDIRECT_URL = 'chat-page'
LOGOUT_REDIRECT_URL = 'login-user'


# PayPal settings
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='xxxxxxxxxxxxxxxxxxx')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='yyyyyyyyyyyyyyyyy')
PAYPAL_BASE_URL = config('PAYPAL_BASE_URL')