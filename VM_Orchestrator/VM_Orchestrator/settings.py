"""
Django settings for VM_Orchestrator project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os, json
import redminelib
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings = json.loads(open(BASE_DIR+'/settings.json').read())
settings['PROJECT']['START_DATE'] = datetime.strptime(settings['PROJECT']['START_DATE'],'%d-%m-%Y')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings['DEBUG']

ALLOWED_HOSTS = settings['ALLOWED_HOSTS']


# Application definition

INSTALLED_APPS = [
    'VM_OrchestratorApp.apps.VmOrchestratorappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VM_Orchestrator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join('VM_OrchestratorApp','templates','VM_OrchestratorApp')],
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

WSGI_APPLICATION = 'VM_Orchestrator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Enviroment variables
os.environ['C_FORCE_ROOT'] = settings['CELERY']['C_FORCE_ROOT']

CELERY_BROKER_URL = settings['CELERY']['BROKER_URL']
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

MONGO_INFO = settings['MONGO']

#Checking of settings for scans
BURP_FOLDER = None
BURP_BLACKLIST = None
INT_USERS_LIST = None
INT_PASS_LIST = None
FFUF_LIST = None
WAPPA_KEY = None
redmine_client = None

if settings['BURP']['bash_folder'] != '':
    if os.path.exists(settings['BURP']['bash_folder']):
        BURP_FOLDER = settings['BURP']['bash_folder']
        BURP_BLACKLIST = settings['BURP']['blacklist_findings']
    else:
        raise Exception("Not valid path for burp suite, if you don't want tou use it just fill it empty in the settings.json file")

if settings['WORDLIST']['ssh_ftp_user'] != '':
    if os.path.exists(settings['WORDLIST']['ssh_ftp_user']):
        INT_USERS_LIST = settings['WORDLIST']['ssh_ftp_user']
    else:
        raise Exception("Not valid path for ssh ftp users list, if you don't want tou use it just fill it empty in the settings.json file")

if settings['WORDLIST']['ssh_ftp_pass'] != '':
    if os.path.exists(settings['WORDLIST']['ssh_ftp_pass']):
        INT_PASS_LIST = settings['WORDLIST']['ssh_ftp_pass']
    else:
        raise Exception("Not valid path for ssh ftp passwords list, if you don't want tou use it just fill it empty in the settings.json file")

if settings['WORDLIST']['ffuf_list'] != '':
    if os.path.exists(settings['WORDLIST']['ffuf_list']):
        FFUF_LIST = settings['WORDLIST']['ffuf_list']
    else:
        raise Exception("Not valid path for ffuf wordlist, if you don't want tou use it just fill it empty in the settings.json file")

if settings['WAPPALIZE_KEY'] != '':
    WAPPA_KEY = settings['WAPPALIZE_KEY']

# Redmine connection
REDMINE_URL = settings['REDMINE']['url']
REDMINE_USER = settings['REDMINE']['user']
REDMINE_PASSWORD = settings['REDMINE']['password']
try:
    if REDMINE_URL != '' and REDMINE_USER != '' and REDMINE_PASSWORD != '':
        redmine_client = redminelib.Redmine(str(REDMINE_URL), username=str(REDMINE_USER), password=str(REDMINE_PASSWORD),
                            requests={'verify': False})
        redmine_client.project.all()[0]
except requests.exceptions.MissingSchema:
    redmine_client = None
    raise Exception("Missing schema for redmine")
except redminelib.exceptions.AuthError:
    redmine_client = None
    raise Exception("Redmine authentication error, check your credentials")
except Exception:
    redmine_client = None
    raise Exception("Somethig went wrong with the redmine, check credencials and url in settings.json configuration file")

nessus_info = settings['NESSUS']
nessus = False
try:
    response = requests.post(nessus_info['URL']+'/session',data={'username':nessus_info['USER'],'password':nessus_info['PASSWORD']},verify=False)
    json_resp = json.loads(response.text)
    if json_resp['token']:
        nessus = True
    if not nessus:
        raise Exception('Couldn\'t connect to the nessus server, check the credentials in the settings file')
except KeyError:
    raise Exception('Couldn\'t connect to the nessus server, check the credentials in the settings file')
    pass
except Exception:
    print('Nessus connection failed, check the settings file or the VPN connection')
    pass