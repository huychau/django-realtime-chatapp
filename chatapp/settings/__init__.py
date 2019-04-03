import os


# Default to dev for safety.
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
if ENVIRONMENT in ('dev', 'test', 'prod'):
    exec(f'from .{ENVIRONMENT} import *')
