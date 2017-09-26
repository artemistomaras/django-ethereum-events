# ==================================
# ETHEREUM CONFIGURATION
# ==================================
ETHEREUM_NODE_HOST = 'localhost'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = False

# ==================================
#   REDIS SETTINGS
# ==================================
REDIS_IP = '127.0.0.1'
REDIS_PORT = 6379
REDIS_CELERY_DATABASE = 0  # Database number that celery uses as a broker
REDIS_CACHE_DATABASE = 1  # Database number that the django cache & session use as a backend

# ==================================
#   CACHE SETTINGS
# ==================================
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{}:{}'.format(REDIS_IP, REDIS_PORT),
        'OPTIONS': {
            'DB': REDIS_CACHE_DATABASE,
        },
        'TIMEOUT': None,  # Never expire
    },
}

# =================================
#   CELERY SETTINGS
# =================================
BROKER_URL = 'redis://{}:{}/{}'.format(REDIS_IP, REDIS_PORT, REDIS_CELERY_DATABASE)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False
CELERY_LOCK_EXPIRE = 60 * 1000 # 1 minute

ETHEREUM_EVENTS = [
    {
        'CONTRACT_ADDRESS': None,
        'EVENT_ABI': None,
        'EVENT_RECEIVER': None
    }
]