import time
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg, Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import User, Task, Submission, TaskAssignment, UserGroup
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer,
    TaskListSerializer, TaskDetailSerializer, AdminTaskSerializer, CreateTaskSerializer,
    ExecuteQuerySerializer, SubmitSolutionSerializer, AdminUserSerializer,
    AssignTaskSerializer, BulkAssignTasksSerializer, AssignTasksToGroupSerializer,
    UserGroupSerializer, UserGroupCreateSerializer,
    LeaderboardEntrySerializer, SettingsSerializer,
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
            'totalTimeSpent': total_time_seconds,    # Для обратной совместимости
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
# 6. ЛОББИ — Назначенные задачи
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_tasks_view(request):
    """GET /user/assigned-tasks — Получить все назначенные задачи пользователя"""
    assignments = TaskAssignment.objects.filter(
        user=request.user,
        completed_at__isnull=True  # Только невыполненные задачи
    ).select_related('task').order_by('assigned_at')

    tasks = []
    for assignment in assignments:
        task = assignment.task
        # Проверяем, решал ли уже эту задачу
        solved = Submission.objects.filter(
            user=request.user,
            task=task,
            is_correct=True
        ).exists()

        tasks.append({
            'id': task.id,
            'title': task.title,
            'difficulty': task.difficulty,
            'points': task.points,
            'solved': solved,
            'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None
        })

    return Response(tasks, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_task_view(request):
    """GET /user/assigned-task — Получить первую назначенную задачу (для обратной совместимости)"""
    assignment = TaskAssignment.objects.filter(
        user=request.user,
        completed_at__isnull=True
    ).select_related('task').first()

    if not assignment:
        return Response(
            {'error': 'Task not assigned'},
            status=status.HTTP_404_NOT_FOUND
        )

    task = assignment.task
    return Response({
        'id': task.id,
        'title': task.title,
        'difficulty': task.difficulty,
        'points': task.points
    }, status=status.HTTP_200_OK)


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
    """
    POST /admin/users/{user_id}/assign — Назначить задачу(и) пользователю
    
    Поддерживает два формата:
    1. Одиночная задача: {"taskId": 3}
    2. Массовое назначение: {"task_ids": [1, 2, 3]}
    
    При назначении автоматически устанавливаются:
    - started_at: текущее время + 1 минута
    - completed_at: текущее время + 24 часа
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Устанавливаем даты: начало через 1 минуту, завершение через 24 часа
    now = timezone.now()
    started_at = now + timedelta(minutes=1)
    completed_at = now + timedelta(hours=24)

    # Проверяем, какой формат данных пришёл
    if 'task_ids' in request.data:
        # Массовое назначение
        serializer = BulkAssignTasksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_ids = serializer.validated_data['task_ids']
        tasks = Task.objects.filter(id__in=task_ids)
        
        if tasks.count() != len(task_ids):
            found_ids = set(tasks.values_list('id', flat=True))
            missing_ids = set(task_ids) - found_ids
            return Response(
                {'detail': f'Tasks not found: {list(missing_ids)}'},
                status=status.HTTP_404_NOT_FOUND
            )

        assigned_count = 0
        for task in tasks:
            assignment, created = TaskAssignment.objects.get_or_create(
                user=user,
                task=task,
                defaults={
                    'started_at': started_at,
                    'completed_at': completed_at
                }
            )
            if created:
                assigned_count += 1

        return Response({
            'success': True,
            'message': f'Назначено задач: {assigned_count}',
            'assigned_count': assigned_count
        }, status=status.HTTP_200_OK)
    else:
        # Одиночная задача (для обратной совместимости)
        serializer = AssignTaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_id = serializer.validated_data['taskId']

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        assignment, created = TaskAssignment.objects.get_or_create(
            user=user,
            task=task,
            defaults={
                'started_at': started_at,
                'completed_at': completed_at
            }
        )

        return Response({
            'success': True,
            'message': 'Задача назначена'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_clear_assignment_view(request, user_id):
    """
    POST /admin/users/{user_id}/clear — Снять назначение(я)
    
    Поддерживает два формата:
    1. Снять все задачи: {} (пустое тело)
    2. Снять конкретную задачу: {"taskId": 3}
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if 'taskId' in request.data:
        # Снять конкретную задачу
        task_id = request.data['taskId']
        deleted_count, _ = TaskAssignment.objects.filter(user=user, task_id=task_id).delete()
        return Response({
            'success': True,
            'message': 'Назначение снято' if deleted_count else 'Назначение не найдено'
        }, status=status.HTTP_200_OK)
    else:
        # Снять все задачи
        TaskAssignment.objects.filter(user=user).delete()
        return Response({
            'success': True,
            'message': 'Все назначения сняты'
        }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAdmin])
def admin_tasks_view(request):
    """
    GET /admin/tasks — Все задачи для админки
    POST /admin/tasks — Создать задачу (принимает camelCase expectedResult)
    """
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = AdminTaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
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
# 8. ГРУППЫ ПОЛЬЗОВАТЕЛЕЙ
# ==========================================

@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_groups_view(request):
    """GET /admin/groups — Список всех групп"""
    groups = UserGroup.objects.all()
    serializer = UserGroupSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_create_group_view(request):
    """POST /admin/groups — Создать группу пользователей"""
    serializer = UserGroupCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    
    # Проверяем уникальность имени
    if UserGroup.objects.filter(name=data['name']).exists():
        return Response(
            {'detail': 'Группа с таким названием уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    group = UserGroup.objects.create(
        name=data['name'],
        description=data.get('description', '')
    )

    # Добавляем пользователей в группу
    user_ids = data.get('user_ids', [])
    if user_ids:
        users = User.objects.filter(id__in=user_ids)
        group.users.set(users)

    return Response({
        'id': group.id,
        'name': group.name,
        'success': True
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdmin])
def admin_group_detail_view(request, group_id):
    """
    GET /admin/groups/{id} — Детали группы
    PUT /admin/groups/{id} — Обновить группу
    DELETE /admin/groups/{id} — Удалить группу
    """
    try:
        group = UserGroup.objects.get(id=group_id)
    except UserGroup.DoesNotExist:
        return Response({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserGroupCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        group.name = data.get('name', group.name)
        group.description = data.get('description', group.description)
        group.save()

        if 'user_ids' in request.data:
            users = User.objects.filter(id__in=data['user_ids'])
            group.users.set(users)

        return Response({
            'id': group.id,
            'name': group.name,
            'success': True
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        group.delete()
        return Response({
            'success': True,
            'message': 'Группа удалена'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_assign_tasks_to_group_view(request, group_id):
    """
    POST /admin/groups/{id}/assign — Назначить задачи всем пользователям группы
    
    Request: {"task_ids": [1, 2, 3]}
    
    При назначении автоматически устанавливаются:
    - started_at: текущее время + 1 минута
    - completed_at: текущее время + 24 часа
    """
    try:
        group = UserGroup.objects.get(id=group_id)
    except UserGroup.DoesNotExist:
        return Response({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AssignTasksToGroupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task_ids = serializer.validated_data['task_ids']
    tasks = Task.objects.filter(id__in=task_ids)

    if tasks.count() != len(task_ids):
        found_ids = set(tasks.values_list('id', flat=True))
        missing_ids = set(task_ids) - found_ids
        return Response(
            {'detail': f'Tasks not found: {list(missing_ids)}'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Устанавливаем даты: начало через 1 минуту, завершение через 24 часа
    now = timezone.now()
    started_at = now + timedelta(minutes=1)
    completed_at = now + timedelta(hours=24)

    users = group.users.all()
    assigned_count = 0

    for user in users:
        for task in tasks:
            assignment, created = TaskAssignment.objects.get_or_create(
                user=user,
                task=task,
                defaults={
                    'started_at': started_at,
                    'completed_at': completed_at
                }
            )
            if created:
                assigned_count += 1

    return Response({
        'success': True,
        'message': f'Назначено {len(task_ids)} задач {users.count()} пользователям',
        'assigned_count': assigned_count,
        'users_count': users.count(),
        'tasks_count': len(task_ids)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_clear_group_assignments_view(request, group_id):
    """
    POST /admin/groups/{id}/clear — Снять все назначения у пользователей группы
    
    Request (опционально): {"task_ids": [1, 2]} — если указаны, снимает только эти задачи
    """
    try:
        group = UserGroup.objects.get(id=group_id)
    except UserGroup.DoesNotExist:
        return Response({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    users = group.users.all()
    
    if 'task_ids' in request.data:
        task_ids = request.data['task_ids']
        deleted_count, _ = TaskAssignment.objects.filter(
            user__in=users,
            task_id__in=task_ids
        ).delete()
    else:
        deleted_count, _ = TaskAssignment.objects.filter(user__in=users).delete()

    return Response({
        'success': True,
        'message': f'Снято назначений: {deleted_count}',
        'deleted_count': deleted_count
    }, status=status.HTTP_200_OK)


# ==========================================
# 9. НАСТРОЙКИ (есть во фронтенде api.ts!)
# ==========================================

# Хранилище настроек (в памяти, для простоты)
_battle_settings = {
    'battle_start': '2026-09-15T10:00:00Z',
    'round_duration_minutes': 120
}


@api_view(['GET', 'PUT'])
@permission_classes([IsAdmin])
def admin_settings_view(request):
    """
    GET /admin/settings — Получить настройки
    PUT /admin/settings — Обновить настройки
    """
    global _battle_settings

    if request.method == 'GET':
        return Response(_battle_settings, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        if 'battle_start' in request.data:
            _battle_settings['battle_start'] = request.data['battle_start']
        if 'round_duration_minutes' in request.data:
            _battle_settings['round_duration_minutes'] = request.data['round_duration_minutes']
        return Response(_battle_settings, status=status.HTTP_200_OK)
