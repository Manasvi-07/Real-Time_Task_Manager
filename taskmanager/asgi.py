"""
ASGI config for taskmanager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
django.setup()

from tasks.middleware import JWTAuthMiddleware
from tasks.routing import websocket_urlpatterns as task_ws_patterns
from chat.routing import websocket_urlpatterns as chat_ws_patterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(task_ws_patterns + chat_ws_patterns)
    ),
})
