import time
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg, Q, Count, Sum

from .models import User, Task, Submission, TaskAssignment
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer,
    TaskListSerializer, TaskDetailSerializer, AdminTaskSerializer, CreateTaskSerializer,
    ExecuteQuerySerializer, SubmitSolutionSerializer, AdminUserSerializer,
    AssignTaskSerializer, LeaderboardEntrySerializer, SettingsSerializer,
)
from .permissions import IsAdmin
from .utils import execute_sql_sandbox, validate_query, compare_results


# ==========================================
# JWT — кастомный формат { token, user }
# ==========================================

def get_tokens_for_user(user):
    """Возвращает токен в формате, ожидаемом фронтендом: { token, user }"""
    refresh = RefreshToken.for_user(user)
    user_data = UserSerializer(user).data
    return {
        'token': str(refresh.access_token),
        'user': user_data
    }


# ==========================================
# 1. АУТЕНТИФИКАЦИЯ
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """POST /api/auth/register — Регистрация"""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    token_data = get_tokens_for_user(user)
    return Response(token_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """POST /api/auth/login — Вход"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Неверный логин или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {'detail': 'Неверный логин или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token_data = get_tokens_for_user(user)
    return Response(token_data, status=status.HTTP_200_OK)


# ==========================================
# 2. ПРОФИЛЬ
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """GET /api/profile — Профиль текущего пользователя"""
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_history_view(request):
    """
    GET /api/profile/history — История решений текущего пользователя.

    Фронтенд ожидает массив объектов:
    [
        {
            "id": 1,
            "task_title": "Найди активных хакеров",
            "difficulty": "easy",
            "execution_time": 0.12,
            "is_correct": true,
            "points_earned": 100
        },
        ...
    ]
    """
    user = request.user

    # Получаем все попытки пользователя, отсортированные по дате (новые первые)
    submissions = Submission.objects.filter(user=user).select_related('task').order_by('-created_at')

    history = []
    for sub in submissions:
        # execution_time_ms → секунды (float)
        execution_time = round((sub.execution_time_ms or 0) / 1000, 2)

        history.append({
            'id': sub.id,
            'task_title': sub.task.title,
            'difficulty': sub.task.difficulty,
            'execution_time': execution_time,
            'is_correct': sub.is_correct,
            'points_earned': sub.points_earned,
        })

    return Response(history, status=status.HTTP_200_OK)


# ==========================================
# 3. ЗАДАЧИ
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])  # Изменено с IsAuthenticated на AllowAny
def task_list_view(request):
    """GET /tasks — Список задач (с полем status)"""
    tasks = Task.objects.all()
    serializer = TaskListSerializer(tasks, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail_view(request, task_id):
    """GET /api/tasks/{id} — Детали задачи"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 4. ВЫПОЛНЕНИЕ И ПРОВЕРКА ЗАПРОСОВ
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_query_view(request, task_id):
    """POST /api/tasks/{id}/execute — Выполнить SQL-запрос (кнопка Run)"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExecuteQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']

    # Валидация запроса
    if not validate_query(query):
        return Response({
            'status': 'error',
            'message': 'Запрещённая операция. Разрешены только SELECT-запросы.'
        }, status=status.HTTP_200_OK)

    # Выполнение в sandbox
    start_time = time.time()
    success, result_or_error = execute_sql_sandbox(
        query=query,
        schema=task.schema,
        tables_data=task.tables
    )
    execution_time = round(time.time() - start_time, 3)

    if success:
        return Response({
            'status': 'success',
            'data': result_or_error,
            'execution_time': execution_time
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': result_or_error
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_solution_view(request, task_id):
    """POST /api/tasks/{id}/submit — Отправить решение на проверку"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubmitSolutionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    time_spent = serializer.validated_data.get('time_spent', 0)  # Время от фронтенда в секундах
    user = request.user

    # Валидация запроса
    if not validate_query(query):
        # Сохраняем неправильную попытку
        Submission.objects.create(
            user=user, task=task, query=query,
            is_correct=False, points_earned=0,
            execution_time_ms=int(time_spent * 1000) if time_spent else None
        )
        return Response({
            'is_correct': False,
            'points_earned': 0,
            'new_total_points': user.total_points,
            'expected_result': task.expected_result
        }, status=status.HTTP_200_OK)

    # Выполнение запроса в sandbox
    start_time = time.time()
    success, result_or_error = execute_sql_sandbox(
        query=query,
        schema=task.schema,
        tables_data=task.tables
    )
    execution_time_ms = int((time.time() - start_time) * 1000)

    # Используем время от фронтенда если оно больше (включает время написания)
    if time_spent > 0:
        execution_time_ms = max(execution_time_ms, int(time_spent * 1000))

    if not success:
        # Ошибка выполнения
        Submission.objects.create(
            user=user, task=task, query=query,
            is_correct=False, points_earned=0,
            execution_time_ms=execution_time_ms
        )
        return Response({
            'is_correct': False,
            'points_earned': 0,
            'new_total_points': user.total_points,
            'expected_result': task.expected_result
        }, status=status.HTTP_200_OK)

    # Сравнение результатов
    is_correct = compare_results(result_or_error, task.expected_result)

    points_earned = 0
    if is_correct:
        # Проверяем, не решал ли уже эту задачу
        already_solved = Submission.objects.filter(
            user=user, task=task, is_correct=True
        ).exists()

        if not already_solved:
            points_earned = task.points
            user.total_points += points_earned
            user.rating += points_earned
            user.save()

    # Сохраняем попытку
    Submission.objects.create(
        user=user, task=task, query=query,
        is_correct=is_correct, points_earned=points_earned,
        execution_time_ms=execution_time_ms
    )

    # Обновляем задание
    try:
        assignment = user.assignment
        if is_correct and not assignment.completed_at:
            from django.utils import timezone
            assignment.completed_at = timezone.now()
            assignment.save()
    except TaskAssignment.DoesNotExist:
        pass

    # Отправляем обновление лидерборда через WebSocket
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        leaderboard_data = get_leaderboard_data()
        async_to_sync(channel_layer.group_send)(
            'leaderboard',
            {
                'type': 'leaderboard_update',
                'data': leaderboard_data
            }
        )
    except Exception:
        pass  # WebSocket не критичен

    return Response({
        'is_correct': is_correct,
        'points_earned': points_earned,
        'new_total_points': user.total_points,
        'expected_result': task.expected_result
    }, status=status.HTTP_200_OK)


# ==========================================
# 5. ЛИДЕРБОРД
# ==========================================

def get_leaderboard_data():
    """Получает данные лидерборда в camelCase формате"""
    users = User.objects.filter(
        Q(total_points__gt=0) | Q(role='participant')
    ).order_by('-total_points')[:50]

    result = []
    for rank, user in enumerate(users, 1):
        solved_count = Submission.objects.filter(
            user=user, is_correct=True
        ).values('task_id').distinct().count()

        # Считаем общее время, потраченное на все правильные решения
        total_time_ms = Submission.objects.filter(
            user=user, is_correct=True, execution_time_ms__isnull=False
        ).aggregate(total=Sum('execution_time_ms'))['total']

        total_time_seconds = round((total_time_ms or 0) / 1000, 2)
        avatar = user.username[:2].upper() if user.username else '??'

        result.append({
            'rank': rank,
            'username': user.username,
            'totalPoints': user.total_points,
            'solvedTasks': solved_count,
            'total_time_spent': total_time_seconds,  # Новое поле
            'totalTimeSpent': total_time_seconds,  # Для обратной совместимости
            'avgTime': round(total_time_seconds / max(solved_count, 1), 2),  # Старое поле
            'avatar': avatar
        })

    return result


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard_view(request):
    """GET /api/leaderboard — Лидерборд"""
    data = get_leaderboard_data()
    return Response(data, status=status.HTTP_200_OK)


# ==========================================
# 6. ЛОББИ — Назначенная задача
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_task_view(request):
    """GET /api/user/assigned-task — Получить назначенную задачу"""
    try:
        assignment = request.user.assignment
        task = assignment.task
        return Response({
            'id': task.id,
            'title': task.title,
            'difficulty': task.difficulty,
            'points': task.points
        }, status=status.HTTP_200_OK)
    except TaskAssignment.DoesNotExist:
        return Response(
            {'error': 'Task not assigned'},
            status=status.HTTP_404_NOT_FOUND
        )


# ==========================================
# 7. АДМИНКА
# ==========================================

@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_users_view(request):
    """GET /api/admin/users — Список пользователей (админ)"""
    users = User.objects.all().order_by('-total_points')
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_assign_task_view(request, user_id):
    """POST /api/admin/users/{user_id}/assign — Назначить задачу (принимает camelCase taskId)"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AssignTaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task_id = serializer.validated_data['taskId']

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    # Создаём или обновляем назначение
    assignment, created = TaskAssignment.objects.update_or_create(
        user=user,
        defaults={
            'task': task,
            'completed_at': None,
        }
    )
    if not assignment.started_at:
        from django.utils import timezone
        assignment.started_at = timezone.now()
        assignment.save()

    return Response({
        'success': True,
        'message': 'Задача назначена'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_clear_assignment_view(request, user_id):
    """POST /api/admin/users/{user_id}/clear — Снять назначение"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    TaskAssignment.objects.filter(user=user).delete()

    return Response({
        'success': True,
        'message': 'Назначение снято'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_tasks_view(request):
    """GET /api/admin/tasks — Все задачи для админки"""
    tasks = Task.objects.all()
    serializer = AdminTaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_create_task_view(request):
    """POST /api/admin/tasks — Создать задачу (принимает camelCase expectedResult)"""
    serializer = CreateTaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    task = Task.objects.create(
        title=data['title'],
        description=data['description'],
        difficulty=data['difficulty'],
        points=data['points'],
        schema=data['schema'],
        tables=data['tables'],
        expected_result=data.get('expectedResult', [])
    )

    return Response({
        'id': task.id,
        'title': task.title,
        'success': True
    }, status=status.HTTP_201_CREATED)


# ==========================================
# 8. НАСТРОЙКИ (есть во фронтенде api.ts!)
# ==========================================

# Хранилище настроек (в памяти, для простоты)
_battle_settings = {
    'battle_start': '2026-09-15T10:00:00Z',
    'round_duration_minutes': 120
}


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_settings_view(request):
    """GET /api/admin/settings — Получить настройки"""
    return Response(_battle_settings, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdmin])
def admin_settings_update_view(request):
    """PUT /api/admin/settings — Обновить настройки"""
    global _battle_settings
    if 'battle_start' in request.data:
        _battle_settings['battle_start'] = request.data['battle_start']
    if 'round_duration_minutes' in request.data:
        _battle_settings['round_duration_minutes'] = request.data['round_duration_minutes']
    return Response(_battle_settings, status=status.HTTP_200_OK)