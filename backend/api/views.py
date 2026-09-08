from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import User, Task, Submission, TaskAssignment
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProfileSerializer, TaskListSerializer, TaskDetailSerializer,
    TaskAdminSerializer, TaskCreateSerializer,
    ExecuteQuerySerializer, SubmitQuerySerializer,
    LeaderboardEntrySerializer, AdminUserSerializer,
    AssignTaskSerializer, AssignedTaskSerializer
)
from .utils import execute_sql_in_sandbox, compare_results


def get_tokens_for_user(user):
    """Генерирует JWT токены для пользователя"""
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
    }


# ==================== AUTH ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'token': tokens['token'],
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Вход в систему"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'token': tokens['token'],
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


# ==================== PROFILE ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Получить данные текущего пользователя"""
    serializer = ProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== TASKS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_list(request):
    """Получить список всех задач"""
    tasks = Task.objects.all()
    serializer = TaskListSerializer(tasks, many=True, context={'user': request.user})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    """Получить детали задачи"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== EXECUTE & SUBMIT ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_query(request, task_id):
    """Выполнить SQL-запрос (кнопка Run)"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExecuteQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']

    result = execute_sql_in_sandbox(
        query=query,
        schema=task.schema,
        tables_data=task.tables
    )

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_query(request, task_id):
    """Отправить решение на проверку"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubmitQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']

    # Выполняем запрос в sandbox
    result = execute_sql_in_sandbox(
        query=query,
        schema=task.schema,
        tables_data=task.tables
    )

    if result['status'] == 'error':
        # Сохраняем неправильную попытку
        Submission.objects.create(
            user=request.user,
            task=task,
            query=query,
            is_correct=False,
            points_earned=0
        )
        return Response({
            'is_correct': False,
            'points_earned': 0,
            'new_total_points': request.user.total_points,
            'expected_result': task.expected_result,
            'error': result.get('message', 'Ошибка выполнения запроса')
        }, status=status.HTTP_200_OK)

    # Сравниваем результаты
    user_data = result.get('data', [])
    expected_data = task.expected_result

    is_correct = compare_results(user_data, expected_data)

    # Начисляем баллы если правильно
    points_earned = 0
    if is_correct:
        # Проверяем, не решал ли уже эту задачу
        already_solved = Submission.objects.filter(
            user=request.user, task=task, is_correct=True
        ).exists()

        if not already_solved:
            points_earned = task.points
            request.user.total_points += points_earned
            request.user.rating += points_earned
            request.user.save()

            # Обновляем задание если есть
            try:
                assignment = request.user.assignment
                assignment.completed_at = timezone.now()
                assignment.save()
            except TaskAssignment.DoesNotExist:
                pass

    # Сохраняем попытку
    execution_time_ms = int(result.get('execution_time', 0) * 1000)
    Submission.objects.create(
        user=request.user,
        task=task,
        query=query,
        is_correct=is_correct,
        points_earned=points_earned,
        execution_time_ms=execution_time_ms
    )

    return Response({
        'is_correct': is_correct,
        'points_earned': points_earned,
        'new_total_points': request.user.total_points,
        'expected_result': task.expected_result
    }, status=status.HTTP_200_OK)


# ==================== LEADERBOARD ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    """Получить топ участников"""
    users = User.objects.filter(
        Q(total_points__gt=0) | Q(role='participant')
    ).order_by('-total_points')[:50]

    result = []
    for rank, user in enumerate(users, 1):
        # Считаем решённые задачи
        solved_count = Submission.objects.filter(
            user=user, is_correct=True
        ).values('task_id').distinct().count()

        # Считаем среднее время
        avg_time = Submission.objects.filter(
            user=user, is_correct=True, execution_time_ms__isnull=False
        ).aggregate(avg=Avg('execution_time_ms'))['avg']

        avg_time_seconds = round((avg_time or 0) / 1000, 2)

        # Генерируем аватар (инициалы)
        avatar = user.username[:2].upper() if user.username else '??'

        result.append({
            'rank': rank,
            'username': user.username,
            'total_points': user.total_points,
            'solved_tasks': solved_count,
            'avg_time': avg_time_seconds,
            'avatar': avatar
        })

    return Response(result, status=status.HTTP_200_OK)


# ==================== ADMIN ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users(request):
    """Получить список всех пользователей (для админки)"""
    if request.user.role != 'admin':
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.all().order_by('username')
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_assign_task(request, user_id):
    """Назначить задачу пользователю"""
    if request.user.role != 'admin':
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AssignTaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task_id = serializer.validated_data['task_id']
    task = Task.objects.get(id=task_id)

    # Создаём или обновляем назначение
    assignment, created = TaskAssignment.objects.update_or_create(
        user=target_user,
        defaults={
            'task': task,
            'assigned_at': timezone.now(),
            'started_at': None,
            'completed_at': None
        }
    )

    return Response({
        'success': True,
        'message': 'Задача назначена'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_clear_assignment(request, user_id):
    """Снять назначение задачи"""
    if request.user.role != 'admin':
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    TaskAssignment.objects.filter(user=target_user).delete()

    return Response({
        'success': True,
        'message': 'Назначение снято'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_assigned_task(request):
    """Получить назначенную задачу (для лобби)"""
    try:
        assignment = request.user.assignment
        serializer = AssignedTaskSerializer(assignment.task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TaskAssignment.DoesNotExist:
        return Response({'error': 'Task not assigned'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_tasks(request):
    """Получить все задачи для админки"""
    if request.user.role != 'admin':
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    tasks = Task.objects.all().order_by('id')
    serializer = TaskAdminSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_task(request):
    """Создать новую задачу"""
    if request.user.role != 'admin':
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        task = serializer.save()
        return Response({
            'id': task.id,
            'title': task.title,
            'success': True
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
