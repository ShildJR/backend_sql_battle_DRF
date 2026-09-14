from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Маршрут только для лидерборда (BattleConsumer пока не нужен)
    re_path(r"ws/leaderboard/?$", consumers.LeaderboardConsumer.as_asgi()),
]
