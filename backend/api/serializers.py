from rest_framework import serializers
from .models import User, Task, Submission, TaskAssignment


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=3)

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Логин должен быть длиннее 3 символов")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role='participant'
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя — camelCase для совместимости с фронтендом"""
    totalPoints = serializers.IntegerField(source='total_points', read_only=True)
    solvedTasks = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 'totalPoints', 'role', 'solvedTasks', 'rank']

    def get_solvedTasks(self, obj):
        return list(
            Submission.objects.filter(
                user=obj, is_correct=True
            ).values_list('task_id', flat=True).distinct()
        )

    def get_rank(self, obj):
        users_above = User.objects.filter(total_points__gt=obj.total_points).count()
        return users_above + 1


class UserProfileSerializer(serializers.ModelSerializer):
    """Полный профиль пользователя — возвращает оба формата (snake_case и camelCase)"""
    totalPoints = serializers.IntegerField(source='total_points', read_only=True)
    total_points = serializers.IntegerField(read_only=True)  # Snake case для совместимости
    solvedTasks = serializers.SerializerMethodField()
    solved_tasks = serializers.SerializerMethodField()  # Snake case для совместимости
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 'totalPoints', 'total_points', 'rank', 'solvedTasks', 'solved_tasks', 'role']

    def get_solvedTasks(self, obj):
        return list(
            Submission.objects.filter(
                user=obj, is_correct=True
            ).values_list('task_id', flat=True).distinct()
        )

    def get_solved_tasks(self, obj):
        return self.get_solvedTasks(obj)

    def get_rank(self, obj):
        users_above = User.objects.filter(total_points__gt=obj.total_points).count()
        return users_above + 1


class TaskListSerializer(serializers.ModelSerializer):
    """Список задач — с полем status для фронтенда"""
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'difficulty', 'points', 'status']

    def get_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            solved = Submission.objects.filter(
                user=request.user, task=obj, is_correct=True
            ).exists()
            return 'solved' if solved else 'unsolved'
        return 'unsolved'


class TaskDetailSerializer(serializers.ModelSerializer):
    """Детали задачи — camelCase для expected_result"""
    expectedResult = serializers.JSONField(source='expected_result')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'difficulty', 'points', 'schema', 'tables', 'expectedResult']


class AdminTaskSerializer(serializers.ModelSerializer):
    """Задачи для админки — camelCase"""
    expectedResult = serializers.JSONField(source='expected_result')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'difficulty', 'points', 'schema', 'tables', 'expectedResult']


class CreateTaskSerializer(serializers.Serializer):
    """Создание задачи — принимает camelCase"""
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'])
    points = serializers.IntegerField()
    schema = serializers.CharField()
    tables = serializers.JSONField()
    expectedResult = serializers.JSONField(required=False, default=list)


class ExecuteQuerySerializer(serializers.Serializer):
    query = serializers.CharField()


class SubmitSolutionSerializer(serializers.Serializer):
    query = serializers.CharField()
    time_spent = serializers.FloatField(required=False, default=0)  # Время в секундах


class AdminUserSerializer(serializers.ModelSerializer):
    """Пользователи для админки — camelCase"""
    totalPoints = serializers.IntegerField(source='total_points', read_only=True)
    assignedTaskId = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 'totalPoints', 'assignedTaskId']

    def get_assignedTaskId(self, obj):
        try:
            assignment = obj.assignment
            return assignment.task_id
        except TaskAssignment.DoesNotExist:
            return None


class AssignTaskSerializer(serializers.Serializer):
    """Назначение задачи — принимает camelCase taskId"""
    taskId = serializers.IntegerField()


class LeaderboardEntrySerializer(serializers.Serializer):
    """Запись лидерборда — camelCase"""
    rank = serializers.IntegerField()
    username = serializers.CharField()
    totalPoints = serializers.IntegerField()
    solvedTasks = serializers.IntegerField()
    avgTime = serializers.FloatField()
    avatar = serializers.CharField()


class SettingsSerializer(serializers.Serializer):
    """Настройки баттла"""
    battle_start = serializers.DateTimeField(required=False)
    round_duration_minutes = serializers.IntegerField(required=False, default=120)