from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register', views.register, name='register'),
    path('auth/login', views.login, name='login'),

    # Profile
    path('profile', views.profile, name='profile'),

    # Tasks
    path('tasks', views.task_list, name='task-list'),
    path('tasks/<int:task_id>', views.task_detail, name='task-detail'),
    path('tasks/<int:task_id>/execute', views.execute_query, name='execute-query'),
    path('tasks/<int:task_id>/submit', views.submit_query, name='submit-query'),

    # Leaderboard
    path('leaderboard', views.leaderboard, name='leaderboard'),

    # User assigned task
    path('user/assigned-task', views.user_assigned_task, name='user-assigned-task'),

    # Admin
    path('admin/users', views.admin_users, name='admin-users'),
    path('admin/users/<int:user_id>/assign', views.admin_assign_task, name='admin-assign-task'),
    path('admin/users/<int:user_id>/clear', views.admin_clear_assignment, name='admin-clear-assignment'),
    path('admin/tasks', views.admin_tasks, name='admin-tasks'),
    path('admin/tasks/create', views.admin_create_task, name='admin-create-task'),
]
