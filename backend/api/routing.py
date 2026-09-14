from django.urls import re_path
from . import consumers
from .BattleConsumer import BattleConsumer

websocket_urlpatterns = [
    re_path(r'ws/leaderboard/?$', consumers.LeaderboardConsumer.as_asgi()),
    re_path(r'ws/battle/?$', BattleConsumer.as_asgi()),
]
