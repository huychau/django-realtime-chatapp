from .base import *


DEBUG = True

INSTALLED_APPS += [
    'django_nose',
]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Config test runner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
