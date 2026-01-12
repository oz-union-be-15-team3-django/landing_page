import socket

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
]

# Debug Toolbar Middleware
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

# 도커 환경에서 내부 IP를 자동으로 찾아 INTERNAL_IPS에 추가
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
if DEBUG:
    INTERNAL_IPS = type("Allips", (), {"__contains__": lambda *args: True})()
