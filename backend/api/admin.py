from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import User, Task, TaskAssignment, UserGroup, Submission
from .forms import BulkAssignForm, CreateGroupForm, EditGroupForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'rating', 'total_points', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = admin.ModelAdmin.fieldsets + (
        ('SQL Battle', {'fields': ('rating', 'total_points', 'role')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-assign/', self.admin_site.admin_view(self.bulk_assign_view), name='api_taskassignment_bulk_assign'),
        ]
        return custom_urls + urls
    
    def bulk_assign_view(self, request):
        """View для массового назначения задач"""
        if request.method == 'POST':
            form = BulkAssignForm(request.POST)
            if form.is_valid():
                assign_type = form.cleaned_data['assign_type']
                tasks = form.cleaned_data['tasks']
                
                if assign_type == 'user':
                    users = form.cleaned_data['users']
                    count = 0
                    for user in users:
                        for task in tasks:
                            _, created = TaskAssignment.objects.get_or_create(
                                user=user,
                                task=task,
                                defaults={'completed_at': None}
                            )
                            if created:
                                count += 1
                    messages.success(request, f'Назначено {len(tasks)} задач {len(users)} пользователям (всего {count} назначений)')
                
                elif assign_type == 'group':
                    group = form.cleaned_data['group']
                    users = group.users.all()
                    count = 0
                    for user in users:
                        for task in tasks:
                            _, created = TaskAssignment.objects.get_or_create(
                                user=user,
                                task=task,
                                defaults={'completed_at': None}
                            )
                            if created:
                                count += 1
                    messages.success(request, f'Назначено {len(tasks)} задач группе "{group.name}" ({len(users)} пользователей, всего {count} назначений)')
                
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


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'user_count', 'created_at']
    search_fields = ['name']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create/', self.admin_site.admin_view(self.create_group_view), name='api_usergroup_create'),
            path('<int:group_id>/edit/', self.admin_site.admin_view(self.edit_group_view), name='api_usergroup_edit'),
            path('<int:group_id>/assign/', self.admin_site.admin_view(self.assign_to_group_view), name='api_usergroup_assign'),
        ]
        return custom_urls + urls
    
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
                tasks = Task.objects.filter(id__in=task_ids)
                users = group.users.all()
                count = 0
                for user in users:
                    for task in tasks:
                        _, created = TaskAssignment.objects.get_or_create(
                            user=user,
                            task=task,
                            defaults={'completed_at': None}
                        )
                        if created:
                            count += 1
                messages.success(request, f'Назначено {len(tasks)} задач {len(users)} пользователям (всего {count} назначений)')
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
    user_count.short_description = 'Количество пользователей'
