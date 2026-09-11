from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь платформы SQL Battle"""
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    total_points = models.IntegerField(default=0, verbose_name='Всего баллов')
    role = models.CharField(
        max_length=20,
        default='participant',
        choices=[('participant', 'Участник'), ('admin', 'Администратор')],
        verbose_name='Роль'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Task(models.Model):
    """Задача для SQL-баттла"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        verbose_name='Сложность'
    )
    points = models.IntegerField(verbose_name='Баллы')
    schema = models.TextField(verbose_name='DDL схема')
    tables = models.JSONField(verbose_name='Структура таблиц с примерами')
    expected_result = models.JSONField(verbose_name='Эталонный результат')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['id']

    def __str__(self):
        return f"[{self.difficulty}] {self.title}"


class Submission(models.Model):
    """Попытка решения задачи"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Пользователь'
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Задача'
    )
    query = models.TextField(verbose_name='SQL-запрос')
    is_correct = models.BooleanField(default=False, verbose_name='Правильно')
    points_earned = models.IntegerField(default=0, verbose_name='Заработанные баллы')
    execution_time_ms = models.IntegerField(null=True, blank=True, verbose_name='Время выполнения (мс)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Попытка решения'
        verbose_name_plural = 'Попытки решений'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({'✓' if self.is_correct else '✗'})"


class TaskAssignment(models.Model):
    """
    Назначение задачи участнику.

    Поля:
    - assigned_at  — когда назначили (auto)
    - started_at   — с какого момента задача доступна пользователю
    - deadline     — до какого момента задача должна быть решена (дедлайн)
    - completed_at — когда пользователь реально решил задачу (NULL = не решена)
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Пользователь'
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Задача'
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата назначения')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Доступна с')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Дедлайн')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    class Meta:
        verbose_name = 'Назначение задачи'
        verbose_name_plural = 'Назначения задач'
        unique_together = ['user', 'task']

    def __str__(self):
        return f"{self.user.username} → {self.task.title}"


class UserGroup(models.Model):
    """Группа пользователей для массового назначения задач"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название группы')
    description = models.TextField(blank=True, verbose_name='Описание')
    users = models.ManyToManyField(User, related_name='user_groups', blank=True, verbose_name='Пользователи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Группа пользователей'
        verbose_name_plural = 'Группы пользователей'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.users.count()} пользователей)"


class BattleSettings(models.Model):
    """
    Настройки турнира. Singleton — в БД всегда ровно одна запись (pk=1).
    """
    battle_start = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Время начала турнира'
    )
    battle_end = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Время окончания турнира'
    )
    round_duration_minutes = models.PositiveIntegerField(
        default=120,
        verbose_name='Длительность раунда (мин)'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Турнир активен'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )

    class Meta:
        verbose_name = 'Настройки турнира'
        verbose_name_plural = 'Настройки турнира'

    def __str__(self):
        return 'Настройки турнира'

    def save(self, *args, **kwargs):
        # Singleton: всегда pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def effective_battle_end(self):
        """Если battle_end не задан, считаем его как battle_start + round_duration."""
        if self.battle_end:
            return self.battle_end
        if self.battle_start:
            from datetime import timedelta
            return self.battle_start + timedelta(minutes=self.round_duration_minutes)
        return None