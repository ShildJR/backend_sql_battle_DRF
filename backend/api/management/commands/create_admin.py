from django.core.management.base import BaseCommand
from api.models import User


class Command(BaseCommand):
    help = 'Создаёт админ-пользователя для SQL Battle'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@sqlbattle.local')
        parser.add_argument('--password', type=str, default='admin123')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING(f'Пользователь {username} уже существует, роль обновлена на admin'))
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            user.role = 'admin'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Админ-пользователь {username} создан успешно!'))
