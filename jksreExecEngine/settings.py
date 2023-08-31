#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   settings.py
@Time    :   2020/05/28 19:35:11
'''

import os
import sys

SECRET_KEY = '6(gx2^%pbz!$h0h=j2e2bmgv1k(_fvnup6pl=)6!tc7t6v5q*s'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from exec_config import *

DEBUG = False

# ================================================================================

APPS_DIR = BASE_DIR+'/apps'
sys.path.append(APPS_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'jkexec',
    'jkhdcollect',
    'jkkubernetes'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jksreExecEngine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'jksreExecEngine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/' # 静态文件访问路径
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/common_static') # 公用，第三方静态文件
]
# 开发过程不使用，通常部署使用 python manage.py collectstatic收集到STATIC_ROOT，方便nginx之类的部署
# 会收集各个app下的静态文件，以及STATICFILES_DIRS的文件到此处
STATIC_ROOT = os.path.join(BASE_DIR, "static")


BASE_LOG_DIR = "/tmp"
LOGGING = {
    'version': 1,  # 保留的参数，默认是1
    'disable_existing_loggers': False,  # 是否禁用已经存在的logger实例

    'filters': {  # 过滤器：可以对日志进行输出时的过滤用的
        'require_debug_true': {  # 在debug=True下产生的一些日志信息，要不要记录日志，需要的话就在handlers中加上这个过滤器，不需要就不加
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {  # 和上面相反
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },

    # 日志输出格式的定义
    'formatters': {
        'jkexec': {     # 错误日志输出格式
            'format': '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
            # 'format': '[%(asctime)s] [%(levelname)s]  %(message)s'
        },
        'console': { #levelname等级，asctime记录时间，module表示日志发生的文件名称，lineno行号，message错误信息
            # 'format': '%(asctime)s %(levelname)s : %(pathname)s [line:%(lineno)d]  %(message)s'
            'format': '%(asctime)s %(levelname)s : %(filename)s [line:%(lineno)d]  %(message)s'
}
    },
    # 处理器：需要处理什么级别的日志及如何处理
    'handlers': {
        'console': { #在控制台输出时的实例
                # entrypoint 或 engine star脚本会动态判断是否替换为DEBUG
                'level': 'ERROR', #日志等级；debug是最低等级，那么只要比它高等级的信息都会被记录
                'filters': ['require_debug_true'], #在debug=True下才会打印在控制台
                'class': 'logging.StreamHandler', #使用的python的logging模块中的StreamHandler来进行输出
                'formatter': 'console'
        },
        'jkexec': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据文件大小自动切
            'filename': "/var/log/jkexec.log",  # 日志文件
            'maxBytes': 1024 * 1024 * 2,  # 日志大小 100M
            'backupCount': 20,  # 备份数为5  xx.log --> xx.log.1 --> xx.log.2 --> xx.log.3
            'formatter': 'jkexec',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'jkexec': {
            'handlers': ['jkexec'],
            'level': 'DEBUG',
            'propagate': True,  # 如果有父级的logger示例，表示不要向上传递日志流
        },
        'console': {
            'handlers': ['console'],
            'propagate': True,  # 如果有父级的logger示例，表示不要向上传递日志流
        },
    },
}

# ========================================DRF REST_FRAMEWORK===============================================
from datetime import timedelta
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}
# simple jwt
SIMPLE_JWT = {
    # 'ACCESS_TOKEN_LIFETIME': timedelta(days=1),      # access_token的持续时间
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),      # access_token的持续时间
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),       # refresh_token的持续时间
    'AUTH_HEADER_TYPES': ('Bearer',),
}
# ========================================DRF 跨域===============================================
# app: 'corsheaders',

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = ('*')
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
    'x-token',
    'token',
)

# ==============================================ElasticSearch==========================================
# ELASTIC_SEARCH = {
#     'host': '192.168.3.130',
#     # 'host': '192.168.1.150',
#     'port': 9200
# }
ELASTIC_SEARCH_INDEX_NAME = 'task'
ELASTIC_SEARCH_INDEX_MAP = {
    'mappings': {
        'properties': {
            'job_num': {
                'type': 'keyword'
            },
            'status': {
                'type': 'keyword'
            },
            'operator': {
                'type': 'keyword'
            },
            'logs': {
                'type': 'text'
            },
            'result': {
                'type': 'object',
                'enabled': False
            },
            'response': {
                'type': 'object',
                'enabled': False
            },
            'create_date': {
                'type': 'date',
                'format': 'yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis'
            }
        }
    }
}
# ========================================jksre mq msg push================================================
# JK_MQ_USER = 'admin'
# JK_MQ_PASSWORD = 'admin' 
# JK_MQ_HOST = '192.168.3.130'
# JK_MQ_PORT = 5672
JK_MQ_VHOST = '/'                        # 不需修改,去rabbitmq新建 vhost: / 即可
JK_MQ_EXCHANGE = '/'                    # 不需修改,去rabbitmq新建 vhost: / 即可
# ===============================================ansible=================================================
ANSIBLE_DEFAULT_GROUP = 'all'
ANSIBLE_HOSTS_FILE = '/etc/ansible/hosts'
ANSIBLE_EXTEND_MODULES = '/usr/share/ansible'
ANSIBLE_REMOTE_USER = 'root'
ANSIBLE_PLAY = 'JK PLAY'
ANSIBLE_SCRIPT_PATH = BASE_DIR + '/script'   # 后续脚本路径可脱离到项目外,若不想更新覆盖
ANSIBLE_PRIVATE_SCRIPT_PATH = BASE_DIR + '/script/__jkstack'

# ===============================================celery====================================================
from kombu import Exchange,Queue
import ssl
CELERY_TIMEZONE='Asia/Shanghai'         #与setting TIME_ZONE应该一致
BROKER_URL = CELERY_MQ_CLUSTER
# SSL start ------------------------------
if ENABLE_CELERY_MQ_CLUSTER_SSL:
    print("rabbitmq ssl is endaled")
    BROKER_USE_SSL =  {
        'keyfile': BASE_DIR + '/sysconfig/cert/client_key.pem',
        'certfile': BASE_DIR + '/sysconfig/cert/client_certificate.pem',
        'ca_certs': BASE_DIR + '/sysconfig/cert/ca_certificate.pem',
        'cert_reqs': ssl.CERT_REQUIRED
    }

    BROKER_LOGIN_METHOD = "EXTERNAL"
# SSL end  ------------------------------

CELERY_TASK_RESULT_EXPIRES = 60 * 20    # 结果过期时间,结果存储有效时间
# CELERYD_TASK_TIME_LIMIT = 120
CELERYD_TASK_SOFT_TIME_LIMIT = WORKER_TASK_TIMEOUT     # 任务超时时间 .单个任务耗时超过此设置将中断
CELERYD_PREFETCH_MULTIPLIER = WORKER_PREFETCH_MULTIPLIER         # celery worker 每次去rabbitmq预取任务的数量
# CELERY_TASK_ACKS_LATE = True          # 任务执行后确认. 若执行中中断可能会重复执行,若非幂等性任务,不建议开启
CELERY_RESULT_BACKEND       = 'amqp'
CELERY_TASK_SERIALIZER = 'json'         # 任务序列化
CELERY_RESULT_SERIALIZER = 'json'       # 结果序列化
CELERY_ACCEPT_CONTENT = ['json']        # 指定接受的内容类型
# CELERYD_CONCURRENCY = 1 if DEBUG else 6    
CELERYD_CONCURRENCY = WORKER_EXEC_CONCURRENCY # celery worker的并发数,也是命令行-c指定的数目 根据服务器配置实际更改
CELERYD_MAX_TASKS_PER_CHILD = 100        # 每个worker执行了多少任务就会死掉，可防止内存泄漏
CELERY_QUEUES = (
    Queue("exec-task",Exchange("exec-task"),routing_key="exec-task"),  # 定义一个队列,用来绑定task任务 
    Queue("collect-task",Exchange("collect-task"),routing_key="collect-task"),  # 定义一个队列,用来绑定task任务 
    # jktask.py  @app.task(bind=True, base=MyTask, queue='devops-task', rate_limit=5)
)


# ========================================saltstack================================================
SALT_MASTER_CONFIG = '/etc/salt/master'     # salt config file 

# ========================================websocket address================================================
# WS_SERVER = ''

# ===========================================smart agent===================================================
SMART_AGENT_SCRIPT_PATH_LINUX = '/tmp/'
SMART_AGENT_SCRIPT_PATH_WINDOWS = 'C:/smart_agent/script/'

# ===========================================rpa mq===================================================
# JK_RPA_REQUEST = 'rpa_request' 
# JK_RPA_RESPONSE = 'rpa_response' 


# ===========================================pika msg push===================================================
if ENABLE_OTHER_MQ_CLUSTER_SSL:
    import re
    PIKA_SSL_CERT = {
        'ssl_options': {
            'certfile': BASE_DIR + '/sysconfig/cert/client_certificate.pem',
            'keyfile': BASE_DIR + '/sysconfig/cert/client_key.pem',
            'ca_certs': BASE_DIR + '/sysconfig/cert/ca_certificate.pem',
            'cert_reqs': ssl.CERT_REQUIRED
            }
        }
    # SSL 只支持一个，通常集群是有SLB的
    PIKA_PUSH_MSG_MQ_CLUSTER = re.findall( r'[0-9]+(?:\.[0-9]+){3}',OTHER_MQ_CLUSTER[0])[0]

else:
    PIKA_PUSH_MSG_MQ_CLUSTER = OTHER_MQ_CLUSTER

