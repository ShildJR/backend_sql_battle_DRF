import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Sum, Q


class LeaderboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer для реалтайм-обновлений лидерборда"""

    async def connect(self):
        self.group_name = "leaderboard"

        user = self.scope.get("user")
        is_auth = getattr(user, "is_authenticated", False)
        print(
            f"👤 [WS Consumer] Пользователь: {getattr(user, 'username', 'Anonymous')}, is_authenticated: {is_auth}"
        )

        if not user or not is_auth:
            print(
                "❌ [WS Consumer] Отказ в доступе: пользователь не аутентифицирован. Закрываю соединение."
            )
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print("✅ [WS Consumer] Соединение принято (accept). Готовлю данные...")

        try:
            leaderboard_data = await self.get_leaderboard()
            await self.send(
                text_data=json.dumps(
                    {"type": "leaderboard_update", "data": leaderboard_data}
                )
            )
            print("✅ [WS Consumer] Данные лидерборда успешно отправлены клиенту.")
        except Exception as e:
            print(f"❌ [WS Consumer] Критическая ошибка при отправке данных: {e}")
            traceback.print_exc()
            await self.close(code=1011)  # Внутренняя ошибка сервера

    async def disconnect(self, close_code):
        """Отключение клиента"""
        print(f"🔌 [WS Consumer] Отключение. Код: {close_code}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def leaderboard_update(self, event):
        await self.send(
            text_data=json.dumps({"type": "leaderboard_update", "data": event["data"]})
        )

    @database_sync_to_async
    def get_leaderboard(self):
        from .models import User, Submission

        users = User.objects.filter(
            Q(total_points__gt=0) | Q(role="participant")
        ).order_by("-total_points")[:50]

        result = []
        for rank, user in enumerate(users, 1):
            solved_count = (
                Submission.objects.filter(user=user, is_correct=True)
                .values("task_id")
                .distinct()
                .count()
            )

            total_time_spent = Submission.objects.filter(
                user=user, is_correct=True, time_spent__isnull=False
            ).aggregate(total=Sum("time_spent"))["total"]

            total_time_seconds = int(total_time_spent or 0)
            avatar = user.username[:2].upper() if user.username else "??"

            result.append(
                {
                    "rank": rank,
                    "username": user.username,
                    "totalPoints": user.total_points,
                    "solvedTasks": solved_count,
                    "total_time_spent": total_time_seconds,
                    "totalTimeSpent": total_time_seconds,
                    "avatar": avatar,
                }
            )

        return result
