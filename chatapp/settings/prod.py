from .base import *


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis://:FR5CPbp23DnnBzJB3gCuw2wbRQwnwLdP@SG-chatapp-20554.servers.mongodirector.com:6379/0')],
        },
    },
}
