from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from .models import User


@database_sync_to_async
def get_user_from_token(token_str):
    """Получает пользователя из JWT-токена"""
    try:
        token = AccessToken(token_str)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        return user
    except Exception:
        return AnonymousUser()


class QueryAuthMiddleware(BaseMiddleware):
    """
    Middleware для аутентификации WebSocket через query-параметр ?token=...

    Фронтенд не может отправлять заголовки через WebSocket, поэтому токен
    передаётся в URL: ws://localhost:8000/ws/leaderboard?token=eyJ...
    """

    async def __call__(self, scope, receive, send):
        # Извлекаем query string
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)

        # Получаем токен из query-параметра
        token_list = query_params.get('token', [])
        token_str = token_list[0] if token_list else None

        if token_str:
            scope['user'] = await get_user_from_token(token_str)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)