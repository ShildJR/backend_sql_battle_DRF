from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация (без авторизации)
    path('auth/register', views.register_view, name='register'),
    path('auth/login', views.login_view, name='login'),

    # Профиль
    path('profile', views.profile_view, name='profile'),

    # Задачи
    path('tasks', views.task_list_view, name='task-list'),
    path('tasks/<int:task_id>', views.task_detail_view, name='task-detail'),
    path('tasks/<int:task_id>/execute', views.execute_query_view, name='execute-query'),
    path('tasks/<int:task_id>/submit', views.submit_solution_view, name='submit-solution'),

    # Лидерборд
    path('leaderboard', views.leaderboard_view, name='leaderboard'),

    # Лобби — назначенная задача
    path('user/assigned-task', views.assigned_task_view, name='assigned-task'),

    # Админка — пользователи
    path('admin/users', views.admin_users_view, name='admin-users'),
    path('admin/users/<int:user_id>/assign', views.admin_assign_task_view, name='admin-assign'),
    path('admin/users/<int:user_id>/clear', views.admin_clear_assignment_view, name='admin-clear'),

    # Админка — задачи
    path('admin/tasks', views.admin_tasks_view, name='admin-tasks'),
    path('admin/tasks/create', views.admin_create_task_view, name='admin-create-task'),

    # Админка — настройки
    path('admin/settings', views.admin_settings_view, name='admin-settings'),
    path('admin/settings/update', views.admin_settings_update_view, name='admin-settings-update'),
]
