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
        user_id = token["user_id"]
        user = User.objects.get(id=user_id)
        return user
    except Exception:
        return AnonymousUser()


class QueryAuthMiddleware(BaseMiddleware):
    """
    Middleware для аутентификации WebSocket через query-параметр ?token=...
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        print(f"🔍 [WS Middleware] Raw query string: '{query_string}'")

        query_params = parse_qs(query_string)
        token_list = query_params.get("token", [])
        token_str = token_list[0] if token_list else None

        print(
            f"🔑 [WS Middleware] Извлеченный токен: {'ЕСТЬ' if token_str else 'ОТСУТСТВУЕТ'}"
        )

        if token_str:
            scope["user"] = await get_user_from_token(token_str)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
