import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from .models import User


class BattleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Извлекаем токен из query-строки
        query_string = self.scope['query_string'].decode()
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[-1].split('&')[0]

        self.user = await self.get_user_from_token(token)

        if self.user is None:
            # Отклоняем соединение, если пользователь не аутентифицирован
            await self.close()
        else:
            await self.accept()
            # Добавляем в группу для рассылки обновлений (опционально)
            self.room_group_name = f'battle_{self.user.id}'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Если фронтенд шлёт сообщения, обработайте их здесь
        pass

    async def battle_update(self, event):
        # Отправка данных клиенту (например, при изменении статуса баттла)
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except Exception:
            return None