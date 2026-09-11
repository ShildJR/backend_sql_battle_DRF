import time
from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Task, Submission, TaskAssignment, UserGroup, BattleSettings
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer,
    TaskListSerializer, TaskDetailSerializer, AdminTaskSerializer, CreateTaskSerializer,
    ExecuteQuerySerializer, SubmitSolutionSerializer, AdminUserSerializer,
    AssignTaskSerializer, BulkAssignTasksSerializer, AssignTasksToGroupSerializer,
    UserGroupSerializer, UserGroupCreateSerializer,
)
from .permissions import IsAdmin
from .utils import execute_sql_sandbox, validate_query, compare_results


# ==========================================
# JWT
# ==========================================

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
        'user': UserSerializer(user).data,
    }


# ==========================================
# 1. АУТЕНТИФИКАЦИЯ
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    return Response(get_tokens_for_user(user), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'detail': 'Неверный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'detail': 'Неверный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)


# ==========================================
# 2. ПРОФИЛЬ
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_history_view(request):
    submissions = (
        Submission.objects
        .filter(user=request.user)
        .select_related('task')
        .order_by('-created_at')
    )

    history = [
        {
            'id': sub.id,
            'task_title': sub.task.title,
            'difficulty': sub.task.difficulty,
            'execution_time': round((sub.execution_time_ms or 0) / 1000, 2),
            'is_correct': sub.is_correct,
            'points_earned': sub.points_earned,
        }
        for sub in submissions
    ]
    return Response(history, status=status.HTTP_200_OK)


# ==========================================
# 3. ЗАДАЧИ
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def task_list_view(request):
    tasks = Task.objects.all()
    serializer = TaskListSerializer(tasks, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 4. ВЫПОЛНЕНИЕ И ПРОВЕРКА
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_query_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExecuteQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']

    if not validate_query(query):
        return Response({
            'status': 'error',
            'message': 'Запрещённая операция. Разрешены только SELECT-запросы.'
        }, status=status.HTTP_200_OK)

    start_time = time.time()
    success, result_or_error = execute_sql_sandbox(
        query=query, schema=task.schema, tables_data=task.tables
    )
    execution_time = round(time.time() - start_time, 3)

    if success:
        return Response({
            'status': 'success',
            'data': result_or_error,
            'execution_time': execution_time,
        }, status=status.HTTP_200_OK)

    return Response({
        'status': 'error',
        'message': result_or_error,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_solution_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubmitSolutionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    time_spent = serializer.validated_data.get('time_spent', 0)
    user = request.user

    # --- Валидация запроса ---
    if not validate_query(query):
        Submission.objects.create(
            user=user, task=task, query=query,
            is_correct=False, points_earned=0,
            execution_time_ms=int(time_spent * 1000) if time_spent else None,
        )
        return Response({
            'is_correct': False,
            'points_earned': 0,
            'new_total_points': user.total_points,
            'expected_result': task.expected_result,
        }, status=status.HTTP_200_OK)

    # --- Выполнение в sandbox ---
    start_time = time.time()
    success, result_or_error = execute_sql_sandbox(
        query=query, schema=task.schema, tables_data=task.tables
    )
    execution_time_ms = int((time.time() - start_time) * 1000)
    if time_spent > 0:
        execution_time_ms = max(execution_time_ms, int(time_spent * 1000))

    if not success:
        Submission.objects.create(
            user=user, task=task, query=query,
            is_correct=False, points_earned=0,
            execution_time_ms=execution_time_ms,
        )
        return Response({
            'is_correct': False,
            'points_earned': 0,
            'new_total_points': user.total_points,
            'expected_result': task.expected_result,
        }, status=status.HTTP_200_OK)

    # --- Сравнение ---
    is_correct = compare_results(result_or_error, task.expected_result)

    points_earned = 0
    if is_correct:
        already_solved = Submission.objects.filter(
            user=user, task=task, is_correct=True
        ).exists()
        if not already_solved:
            points_earned = task.points
            user.total_points += points_earned
            user.rating += points_earned
            user.save(update_fields=['total_points', 'rating'])

    # --- Сохраняем попытку ---
    Submission.objects.create(
        user=user, task=task, query=query,
        is_correct=is_correct, points_earned=points_earned,
        execution_time_ms=execution_time_ms,
    )

    # --- Отмечаем назначение выполненным (исправлено: related_name = 'assignments') ---
    if is_correct:
        assignment = TaskAssignment.objects.filter(
            user=user, task=task, completed_at__isnull=True
        ).first()
        if assignment:
            assignment.completed_at = timezone.now()
            assignment.save(update_fields=['completed_at'])

    # --- Обновляем лидерборд по WS ---
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                'leaderboard',
                {'type': 'leaderboard_update', 'data': get_leaderboard_data()}
            )
    except Exception:
        pass

    return Response({
        'is_correct': is_correct,
        'points_earned': points_earned,
        'new_total_points': user.total_points,
        'expected_result': task.expected_result,
    }, status=status.HTTP_200_OK)


# ==========================================
# 5. ЛИДЕРБОРД
# ==========================================

def get_leaderboard_data():
    users = (
        User.objects
        .filter(Q(total_points__gt=0) | Q(role='participant'))
        .order_by('-total_points')[:50]
    )

    result = []
    for rank, user in enumerate(users, 1):
        solved_count = (
            Submission.objects
            .filter(user=user, is_correct=True)
            .values('task_id').distinct().count()
        )
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
            'total_time_spent': total_time_seconds,
            'totalTimeSpent': total_time_seconds,
            'avgTime': round(total_time_seconds / max(solved_count, 1), 2),
            'avatar': avatar,
        })
    return result


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard_view(request):
    return Response(get_leaderboard_data(), status=status.HTTP_200_OK)


# ==========================================
# 6. ЛОББИ — назначенные задачи
# ==========================================

def _active_assignments_qs(user):
    """
    Возвращает QuerySet активных назначений пользователя:
      - ещё не решены (completed_at IS NULL)
      - уже доступны (started_at IS NULL OR started_at <= now)
      - не просрочены (deadline IS NULL OR deadline > now)
    """
    now = timezone.now()
    return (
        TaskAssignment.objects
        .filter(user=user, completed_at__isnull=True)
        .filter(Q(started_at__isnull=True) | Q(started_at__lte=now))
        .filter(Q(deadline__isnull=True) | Q(deadline__gte=now))
        .select_related('task')
        .order_by('assigned_at')
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_tasks_view(request):
    """GET /api/user/assigned-tasks — все активные назначенные задачи"""
    assignments = _active_assignments_qs(request.user)

    tasks = []
    for assignment in assignments:
        task = assignment.task
        solved = Submission.objects.filter(
            user=request.user, task=task, is_correct=True
        ).exists()
        tasks.append({
            'id': task.id,
            'title': task.title,
            'difficulty': task.difficulty,
            'points': task.points,
            'solved': solved,
            'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None,
            'deadline': assignment.deadline.isoformat() if assignment.deadline else None,
        })
    return Response(tasks, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_task_view(request):
    """GET /api/user/assigned-task — первая активная назначенная задача"""
    assignment = _active_assignments_qs(request.user).first()

    if not assignment:
        # 404 — это нормальный ответ, фронт трактует его как "задачи нет"
        return Response({'error': 'Task not assigned'}, status=status.HTTP_404_NOT_FOUND)

    task = assignment.task
    return Response({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'difficulty': task.difficulty,
        'points': task.points,
        'deadline': assignment.deadline.isoformat() if assignment.deadline else None,
    }, status=status.HTTP_200_OK)


# ==========================================
# 7. АДМИНКА — пользователи и назначения
# ==========================================

@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_users_view(request):
    users = User.objects.all().order_by('-total_points')
    return Response(AdminUserSerializer(users, many=True).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_assign_task_view(request, user_id):
    """
    POST /api/admin/users/{user_id}/assign
    Поддерживает:
      - {"taskId": 3}            — одиночное назначение
      - {"task_ids": [1, 2, 3]}  — массовое назначение
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    started_at = now + timedelta(minutes=1)
    deadline = now + timedelta(hours=24)

    if 'task_ids' in request.data:
        serializer = BulkAssignTasksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_ids = serializer.validated_data['task_ids']
        tasks = Task.objects.filter(id__in=task_ids)

        if tasks.count() != len(task_ids):
            found_ids = set(tasks.values_list('id', flat=True))
            return Response(
                {'detail': f'Tasks not found: {list(set(task_ids) - found_ids)}'},
                status=status.HTTP_404_NOT_FOUND
            )

        assigned_count = 0
        for task in tasks:
            _, created = TaskAssignment.objects.get_or_create(
                user=user, task=task,
                defaults={'started_at': started_at, 'deadline': deadline},
            )
            if created:
                assigned_count += 1

        return Response({
            'success': True,
            'message': f'Назначено задач: {assigned_count}',
            'assigned_count': assigned_count,
        }, status=status.HTTP_200_OK)

    # Одиночное назначение
    serializer = AssignTaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = Task.objects.get(id=serializer.validated_data['taskId'])
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    TaskAssignment.objects.get_or_create(
        user=user, task=task,
        defaults={'started_at': started_at, 'deadline': deadline},
    )
    return Response({'success': True, 'message': 'Задача назначена'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_clear_assignment_view(request, user_id):
    """
    POST /api/admin/users/{user_id}/clear
      - {}               — снять все назначения
      - {"taskId": 3}    — снять конкретную
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if 'taskId' in request.data:
        deleted, _ = TaskAssignment.objects.filter(
            user=user, task_id=request.data['taskId']
        ).delete()
        return Response({
            'success': True,
            'message': 'Назначение снято' if deleted else 'Назначение не найдено',
        }, status=status.HTTP_200_OK)

    TaskAssignment.objects.filter(user=user).delete()
    return Response({'success': True, 'message': 'Все назначения сняты'}, status=status.HTTP_200_OK)


# ==========================================
# 8. АДМИНКА — задачи
# ==========================================

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

    return Response(AdminTaskSerializer(Task.objects.all(), many=True).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_create_task_view(request):
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
        expected_result=data.get('expectedResult', []),
    )
    return Response({'id': task.id, 'title': task.title, 'success': True},
                    status=status.HTTP_201_CREATED)


# ==========================================
# 9. АДМИНКА — группы
# ==========================================

@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_groups_view(request):
    return Response(UserGroupSerializer(UserGroup.objects.all(), many=True).data,
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_create_group_view(request):
    serializer = UserGroupCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    if UserGroup.objects.filter(name=data['name']).exists():
        return Response({'detail': 'Группа с таким названием уже существует'},
                        status=status.HTTP_400_BAD_REQUEST)

    group = UserGroup.objects.create(
        name=data['name'],
        description=data.get('description', ''),
    )
    user_ids = data.get('user_ids', [])
    if user_ids:
        group.users.set(User.objects.filter(id__in=user_ids))

    return Response({'id': group.id, 'name': group.name, 'success': True},
                    status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdmin])
def admin_group_detail_view(request, group_id):
    try:
        group = UserGroup.objects.get(id=group_id)
    except UserGroup.DoesNotExist:
        return Response({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserGroupSerializer(group).data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = UserGroupCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        group.name = data.get('name', group.name)
        group.description = data.get('description', group.description)
        group.save()

        if 'user_ids' in request.data:
            group.users.set(User.objects.filter(id__in=data['user_ids']))

        return Response({'id': group.id, 'name': group.name, 'success': True},
                        status=status.HTTP_200_OK)

    group.delete()
    return Response({'success': True, 'message': 'Группа удалена'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_assign_tasks_to_group_view(request, group_id):
    """POST /api/admin/groups/{group_id}/assign — назначить задачи всем участникам группы"""
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
        return Response(
            {'detail': f'Tasks not found: {list(set(task_ids) - found_ids)}'},
            status=status.HTTP_404_NOT_FOUND
        )

    now = timezone.now()
    started_at = now + timedelta(minutes=1)
    deadline = now + timedelta(hours=24)

    users = list(group.users.all())
    assigned_count = 0
    for user in users:
        for task in tasks:
            _, created = TaskAssignment.objects.get_or_create(
                user=user, task=task,
                defaults={'started_at': started_at, 'deadline': deadline},
            )
            if created:
                assigned_count += 1

    return Response({
        'success': True,
        'message': f'Назначено {len(task_ids)} задач {len(users)} пользователям',
        'assigned_count': assigned_count,
        'users_count': len(users),
        'tasks_count': len(task_ids),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_clear_group_assignments_view(request, group_id):
    """POST /api/admin/groups/{group_id}/clear — снять назначения у группы"""
    try:
        group = UserGroup.objects.get(id=group_id)
    except UserGroup.DoesNotExist:
        return Response({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    users = group.users.all()
    qs = TaskAssignment.objects.filter(user__in=users)

    if 'task_ids' in request.data:
        qs = qs.filter(task_id__in=request.data['task_ids'])

    deleted, _ = qs.delete()
    return Response({
        'success': True,
        'message': f'Снято назначений: {deleted}',
        'deleted_count': deleted,
    }, status=status.HTTP_200_OK)


# ==========================================
# 10. НАСТРОЙКИ (БД, singleton)
# ==========================================

def _serialize_settings(s: 'BattleSettings') -> dict:
    return {
        'battle_start': s.battle_start.isoformat() if s.battle_start else None,
        'battle_end': s.effective_battle_end.isoformat() if s.effective_battle_end else None,
        'round_duration_minutes': s.round_duration_minutes,
        'is_active': s.is_active,
        'updated_at': s.updated_at.isoformat() if s.updated_at else None,
    }


def _parse_dt(value):
    """Парсит ISO-8601 строку в aware datetime или возвращает None."""
    if not value:
        return None
    from django.utils.dateparse import parse_datetime
    dt = parse_datetime(value)
    if dt is None:
        # пробуем через fromisoformat — поддерживает "Z" в новых Python
        try:
            from datetime import datetime, timezone as dt_timezone
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except Exception:
            return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt



@api_view(['GET'])
@permission_classes([AllowAny])
def public_settings_view(request):
    """GET /api/settings — публичные настройки турнира (для лобби)."""
    s = BattleSettings.get_solo()
    return Response({
        'battle_start': s.battle_start.isoformat() if s.battle_start else None,
        'battle_end': s.effective_battle_end.isoformat() if s.effective_battle_end else None,
        'round_duration_minutes': s.round_duration_minutes,
        'is_active': s.is_active,
    }, status=status.HTTP_200_OK)


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
