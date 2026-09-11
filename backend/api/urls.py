from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация (без авторизации)
    path('auth/register', views.register_view, name='register'),
    path('auth/login', views.login_view, name='login'),

    # Профиль
    path('profile', views.profile_view, name='profile'),
    path('profile/history', views.profile_history_view, name='profile-history'),

    # Задачи
    path('tasks', views.task_list_view, name='task-list'),
    path('tasks/<int:task_id>', views.task_detail_view, name='task-detail'),
    path('tasks/<int:task_id>/execute', views.execute_query_view, name='execute-query'),
    path('tasks/<int:task_id>/submit', views.submit_solution_view, name='submit-solution'),

    # Лидерборд
    path('leaderboard', views.leaderboard_view, name='leaderboard'),

    # Лобби — назначенные задачи
    path('user/assigned-tasks', views.assigned_tasks_view, name='assigned-tasks'),
    path('user/assigned-task', views.assigned_task_view, name='assigned-task'),

    # Админка — пользователи
    path('admin/users', views.admin_users_view, name='admin-users'),
    path('admin/users/<int:user_id>/assign', views.admin_assign_task_view, name='admin-assign'),
    path('admin/users/<int:user_id>/clear', views.admin_clear_assignment_view, name='admin-clear'),

    # Админка — задачи
    path('admin/tasks', views.admin_tasks_view, name='admin-tasks'),
    path('admin/tasks/create', views.admin_create_task_view, name='admin-create-task'),

    # Админка — группы пользователей
    path('admin/groups', views.admin_groups_view, name='admin-groups'),
    path('admin/groups/create', views.admin_create_group_view, name='admin-create-group'),
    path('admin/groups/<int:group_id>', views.admin_group_detail_view, name='admin-group-detail'),
    path('admin/groups/<int:group_id>/assign', views.admin_assign_tasks_to_group_view, name='admin-assign-group'),
    path('admin/groups/<int:group_id>/clear', views.admin_clear_group_assignments_view, name='admin-clear-group'),

    # Админка — настройки
    path('admin/settings', views.admin_settings_view, name='admin-settings'),
    path('admin/settings/update', views.admin_settings_update_view, name='admin-settings-update'),
]
