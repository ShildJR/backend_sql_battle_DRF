from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from .models import User, Task, TaskAssignment, UserGroup, Submission
from .forms import BulkAssignForm, CreateGroupForm, EditGroupForm


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
    list_filter = ['task', 'user']
    search_fields = ['user__username', 'task__title']
    change_list_template = 'admin/api/taskassignment/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-assign/', self.admin_site.admin_view(self.bulk_assign_view),
                 name='api_taskassignment_bulk_assign'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Добавляем кнопку 'Массовое назначение' в список"""
        extra_context = extra_context or {}
        extra_context['show_bulk_assign_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def bulk_assign_view(self, request):
        """View для массового назначения задач"""
        if request.method == 'POST':
            form = BulkAssignForm(request.POST)
            if form.is_valid():
                assign_type = form.cleaned_data['assign_type']
                tasks = form.cleaned_data['tasks']

                # Устанавливаем даты: начало через 1 минуту, завершение через 24 часа
                now = timezone.now()
                started_at = now + timedelta(minutes=1)
                completed_at = now + timedelta(hours=24)

                if assign_type == 'user':
                    users = form.cleaned_data['users']
                    count = 0
                    for user in users:
                        for task in tasks:
                            _, created = TaskAssignment.objects.get_or_create(
                                user=user,
                                task=task,
                                defaults={
                                    'started_at': started_at,
                                    'completed_at': completed_at
                                }
                            )
                            if created:
                                count += 1
                    messages.success(request,
                                     f'Назначено {len(tasks)} задач {len(users)} пользователям (всего {count} назначений)')

                elif assign_type == 'group':
                    group = form.cleaned_data['group']
                    users = group.users.all()
                    count = 0
                    for user in users:
                        for task in tasks:
                            _, created = TaskAssignment.objects.get_or_create(
                                user=user,
                                task=task,
                                defaults={
                                    'started_at': started_at,
                                    'completed_at': completed_at
                                }
                            )
                            if created:
                                count += 1
                    messages.success(request,
                                     f'Назначено {len(tasks)} задач группе "{group.name}" ({len(users)} пользователей, всего {count} назначений)')

                return HttpResponseRedirect('../')
        else:
            form = BulkAssignForm()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Массовое назначение задач',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/api/taskassignment/bulk_assign.html', context)


from django.utils.html import format_html


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'user_count', 'assign_tasks_button', 'edit_group_button', 'created_at']
    list_display_links = ['name']
    search_fields = ['name']
    change_list_template = 'admin/api/usergroup/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create/', self.admin_site.admin_view(self.create_group_view), name='api_usergroup_create'),
            path('<int:group_id>/edit/', self.admin_site.admin_view(self.edit_group_view), name='api_usergroup_edit'),
            path('<int:group_id>/assign/', self.admin_site.admin_view(self.assign_to_group_view),
                 name='api_usergroup_assign'),
        ]
        return custom_urls + urls

    def assign_tasks_button(self, obj):
        """Кнопка для назначения задач группе"""
        return format_html(
            '<a class="button" style="background: #417690; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 4px; margin-right: 5px;" '
            'href="{}">📋 Назначить задачи</a>',
            f'{obj.id}/assign/'
        )

    assign_tasks_button.short_description = 'Назначить задачи'

    def edit_group_button(self, obj):
        """Кнопка для редактирования группы"""
        return format_html(
            '<a class="button" style="background: #79aec8; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 4px;" '
            'href="{}">✏️ Редактировать</a>',
            f'{obj.id}/edit/'
        )

    edit_group_button.short_description = 'Действия'

    def create_group_view(self, request):
        """View для создания группы"""
        if request.method == 'POST':
            form = CreateGroupForm(request.POST)
            if form.is_valid():
                group = UserGroup.objects.create(
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data.get('description', '')
                )
                users = form.cleaned_data.get('users', [])
                if users:
                    group.users.set(users)
                messages.success(request, f'Группа "{group.name}" создана ({len(users)} пользователей)')
                return HttpResponseRedirect('../')
        else:
            form = CreateGroupForm()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Создать группу пользователей',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/api/usergroup/create.html', context)

    def edit_group_view(self, request, group_id):
        """View для редактирования группы"""
        try:
            group = UserGroup.objects.get(id=group_id)
        except UserGroup.DoesNotExist:
            messages.error(request, 'Группа не найдена')
            return HttpResponseRedirect('../')

        if request.method == 'POST':
            form = EditGroupForm(request.POST)
            if form.is_valid():
                group.name = form.cleaned_data['name']
                group.description = form.cleaned_data.get('description', '')
                group.save()
                users = form.cleaned_data.get('users', [])
                group.users.set(users)
                messages.success(request, f'Группа "{group.name}" обновлена')
                return HttpResponseRedirect('../../')
        else:
            form = EditGroupForm(initial={
                'name': group.name,
                'description': group.description,
                'users': group.users.all()
            })

        context = {
            **self.admin_site.each_context(request),
            'title': f'Редактировать группу: {group.name}',
            'form': form,
            'group': group,
            'opts': self.model._meta,
        }
        return render(request, 'admin/api/usergroup/edit.html', context)

    def assign_to_group_view(self, request, group_id):
        """View для назначения задач группе"""
        try:
            group = UserGroup.objects.get(id=group_id)
        except UserGroup.DoesNotExist:
            messages.error(request, 'Группа не найдена')
            return HttpResponseRedirect('../../')

        if request.method == 'POST':
            task_ids = request.POST.getlist('tasks')
            if not task_ids:
                messages.error(request, 'Выберите хотя бы одну задачу')
            else:
                # Устанавливаем даты: начало через 1 минуту, завершение через 24 часа
                now = timezone.now()
                started_at = now + timedelta(minutes=1)
                completed_at = now + timedelta(hours=24)

                tasks = Task.objects.filter(id__in=task_ids)
                users = group.users.all()
                count = 0
                for user in users:
                    for task in tasks:
                        _, created = TaskAssignment.objects.get_or_create(
                            user=user,
                            task=task,
                            defaults={
                                'started_at': started_at,
                                'completed_at': completed_at
                            }
                        )
                        if created:
                            count += 1
                messages.success(request,
                                 f'Назначено {len(tasks)} задач {len(users)} пользователям (всего {count} назначений)')
                return HttpResponseRedirect('../../')

        tasks = Task.objects.all()
        context = {
            **self.admin_site.each_context(request),
            'title': f'Назначить задачи группе: {group.name}',
            'group': group,
            'tasks': tasks,
            'opts': self.model._meta,
        }
        return render(request, 'admin/api/usergroup/assign.html', context)

    def user_count(self, obj):
        return obj.users.count()

    user_count.short_description = 'Пользователей'

    def changelist_view(self, request, extra_context=None):
        """Добавляем кнопку 'Создать группу' в список"""
        extra_context = extra_context or {}
        extra_context['show_create_button'] = True
        return super().changelist_view(request, extra_context=extra_context)