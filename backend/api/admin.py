from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Task, Submission, TaskAssignment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'rating', 'total_points', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SQL Battle', {'fields': ('rating', 'total_points', 'role')}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'points', 'created_at']
    list_filter = ['difficulty']
    search_fields = ['title', 'description']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'is_correct', 'points_earned', 'execution_time_ms', 'created_at']
    list_filter = ['is_correct', 'task']
    search_fields = ['user__username']


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'assigned_at', 'started_at', 'completed_at']
    list_filter = ['task']
    search_fields = ['user__username']
