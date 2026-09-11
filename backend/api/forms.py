from django import forms
from .models import User, Task, UserGroup, TaskAssignment


class BulkAssignForm(forms.Form):
    """Форма для массового назначения задач"""

    ASSIGN_TYPE_CHOICES = [
        ('user', 'Пользователю'),
        ('group', 'Группе пользователей'),
    ]

    assign_type = forms.ChoiceField(
        choices=ASSIGN_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='user',
        label='Тип назначения'
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='participant'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Пользователи'
    )

    group = forms.ModelChoiceField(
        queryset=UserGroup.objects.all(),
        required=False,
        label='Группа',
        empty_label='Выберите группу...'
    )

    tasks = forms.ModelMultipleChoiceField(
        queryset=Task.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Задачи'
    )

    def clean(self):
        cleaned_data = super().clean()
        assign_type = cleaned_data.get('assign_type')
        users = cleaned_data.get('users')
        group = cleaned_data.get('group')

        if assign_type == 'user' and not users:
            raise forms.ValidationError('Выберите хотя бы одного пользователя')

        if assign_type == 'group' and not group:
            raise forms.ValidationError('Выберите группу')

        return cleaned_data


class CreateGroupForm(forms.Form):
    """Форма для создания группы пользователей"""

    name = forms.CharField(
        max_length=100,
        label='Название группы'
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Описание'
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='participant'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Пользователи'
    )


class EditGroupForm(forms.Form):
    """Форма для редактирования группы пользователей"""

    name = forms.CharField(
        max_length=100,
        label='Название группы'
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Описание'
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='participant'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Пользователи'
    )