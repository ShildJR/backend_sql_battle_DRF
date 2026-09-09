import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sql_battle.settings')

django_asgi_app = get_asgi_application()

from api.routing import websocket_urlpatterns
from api.middleware import QueryAuthMiddleware

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': QueryAuthMiddleware(URLRouter(websocket_urlpatterns)),
})
