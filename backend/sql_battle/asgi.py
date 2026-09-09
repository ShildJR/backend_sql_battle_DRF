import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from api.routing import websocket_urlpatterns  # <-- единственный источник правды

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sql_battle.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(websocket_urlpatterns),
})