import json
from os import pardir, path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(
    path.abspath(path.join(__file__, pardir))
))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wm82)$7ay(ya#g788(4s#hq1w2cynlt$+2ay_noapdj-#6h7xl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS = (
    'django_ethereum_events',
    'solo'
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CELERY_ALWAYS_EAGER = True

TEST_EVENT_ABI = """
{
  "anonymous": false,
  "inputs": [
    {
      "indexed": true,
      "name": "_from",
      "type": "address"
    },
    {
      "indexed": true,
      "name": "_id",
      "type": "bytes32"
    },
    {
      "indexed": false,
      "name": "_value",
      "type": "uint256"
    }
  ],
  "name": "Deposit",
  "type": "event"
}
"""

# ==================================
# ETHEREUM CONFIGURATION
# ==================================
ETHEREUM_NODE_HOST = 'localhost'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = False

ETHEREUM_EVENTS = [
    {
        'CONTRACT_ADDRESS': '0x0xF54cA23D911fA34ce2FF5F693eaaf83E80576fDe',
        'EVENT_ABI': json.loads(TEST_EVENT_ABI),
        'EVENT_RECEIVER': 'django_ethereum_events.tests' +
                          '.test_event_receivers.DepositEventReceiver'
    }
]
