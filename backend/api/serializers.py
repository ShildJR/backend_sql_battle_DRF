from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Task, Submission, TaskAssignment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 'total_points', 'role']
        read_only_fields = ['id', 'rating', 'total_points', 'role']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует')
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует')
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
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Неверное имя пользователя или пароль')
        if not user.is_active:
            raise serializers.ValidationError('Пользователь деактивирован')
        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    solved_tasks = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 'total_points', 'rank', 'solved_tasks', 'role']

    def get_rank(self, obj):
        rank = User.objects.filter(total_points__gt=obj.total_points).count() + 1
        return rank

    def get_solved_tasks(self, obj):
        task_ids = list(
            Submission.objects.filter(
                user=obj, is_correct=True
            ).values_list('task_id', flat=True).distinct()
        )
        return task_ids


class TaskListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'difficulty', 'points', 'status']

    def get_status(self, obj):
        user = self.context.get('user')
        if user:
            solved = Submission.objects.filter(
                user=user, task=obj, is_correct=True
            ).exists()
            return 'solved' if solved else 'unsolved'
        return 'unsolved'


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'difficulty', 'points', 'schema', 'tables']


class TaskAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'difficulty', 'points', 'description', 'schema', 'tables', 'expected_result']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'difficulty', 'points', 'schema', 'tables', 'expected_result']


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'query', 'is_correct', 'points_earned', 'execution_time_ms', 'created_at']


class ExecuteQuerySerializer(serializers.Serializer):
    query = serializers.CharField()

    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError('Запрос не может быть пустым')
        return value


class SubmitQuerySerializer(serializers.Serializer):
    query = serializers.CharField()

    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError('Запрос не может быть пустым')
        return value


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    username = serializers.CharField()
    total_points = serializers.IntegerField()
    solved_tasks = serializers.IntegerField()
    avg_time = serializers.FloatField()
    avatar = serializers.CharField()


class AdminUserSerializer(serializers.ModelSerializer):
    assigned_task_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 'total_points', 'assigned_task_id']

    def get_assigned_task_id(self, obj):
        try:
            assignment = obj.assignment
            return assignment.task_id
        except TaskAssignment.DoesNotExist:
            return None


class AssignTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()

    def validate_task_id(self, value):
        if not Task.objects.filter(id=value).exists():
            raise serializers.ValidationError('Задача не найдена')
        return value


class AssignedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'difficulty', 'points']
