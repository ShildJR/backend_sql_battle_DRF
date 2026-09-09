import json
from channels.generic.websocket import AsyncWebSocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Avg, Q
from django.contrib.auth.models import AnonymousUser


class LeaderboardConsumer(AsyncWebSocketConsumer):
    """WebSocket consumer для реалтайм-обновлений лидерборда (camelCase)"""

    async def connect(self):
        """Подключение клиента"""
        # Получаем пользователя из scope (установлен middleware)
        self.user = self.scope.get('user', AnonymousUser())
        
        self.group_name = 'leaderboard'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Отправляем текущий лидерборд при подключении
        leaderboard_data = await self.get_leaderboard()
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'data': leaderboard_data
        }))

    async def disconnect(self, close_code):
        """Отключение клиента"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Обработка входящих сообщений (не используется)"""
        pass

    async def leaderboard_update(self, event):
        """Обработка события обновления лидерборда"""
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_leaderboard(self):
        """Получает данные лидерборда из БД — camelCase для совместимости с фронтендом"""
        from .models import User, Submission

        users = User.objects.filter(
            Q(total_points__gt=0) | Q(role='participant')
        ).order_by('-total_points')[:50]

        result = []
        for rank, user in enumerate(users, 1):
            solved_count = Submission.objects.filter(
                user=user, is_correct=True
            ).values('task_id').distinct().count()

            avg_time = Submission.objects.filter(
                user=user, is_correct=True, execution_time_ms__isnull=False
            ).aggregate(avg=Avg('execution_time_ms'))['avg']

            avg_time_seconds = round((avg_time or 0) / 1000, 2)
            avatar = user.username[:2].upper() if user.username else '??'

            # camelCase для совместимости с фронтендом
            result.append({
                'rank': rank,
                'username': user.username,
                'totalPoints': user.total_points,
                'solvedTasks': solved_count,
                'avgTime': avg_time_seconds,
                'avatar': avatar
            })

        return result
