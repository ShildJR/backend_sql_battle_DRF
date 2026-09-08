# SQL Battle Backend (Django)

Бэкенд для платформы SQL-баттлов на Django REST Framework.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

### 3. Миграции и запуск

```bash
python manage.py migrate
python manage.py loaddata api/fixtures/tasks.json  # Загрузить примеры задач
python manage.py createsuperuser  # Создать администратора
python manage.py runserver 0.0.0.0:8000
```

### 4. Создание админ-пользователя через shell

```python
python manage.py shell
>>> from api.models import User
>>> admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin_password')
>>> admin.role = 'admin'
>>> admin.save()
```

## 📁 Структура проекта

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── sql_battle/          # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── api/                 # Основное приложение
    ├── models.py        # Модели БД
    ├── serializers.py   # DRF сериализаторы
    ├── views.py         # API-представления
    ├── urls.py          # Маршруты API
    ├── consumers.py     # WebSocket consumers
    ├── routing.py       # WebSocket маршруты
    ├── utils.py         # Sandbox для SQL
    ├── permissions.py   # Кастомные разрешения
    ├── admin.py         # Django Admin
    └── fixtures/        # Тестовые данные
```

## 🔌 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/profile` | Профиль |
| GET | `/api/tasks` | Список задач |
| GET | `/api/tasks/{id}` | Детали задачи |
| POST | `/api/tasks/{id}/execute` | Выполнить запрос |
| POST | `/api/tasks/{id}/submit` | Отправить решение |
| GET | `/api/leaderboard` | Лидерборд |
| GET | `/api/user/assigned-task` | Назначенная задача |
| GET | `/api/admin/users` | Пользователи (админ) |
| POST | `/api/admin/users/{id}/assign` | Назначить задачу |
| POST | `/api/admin/users/{id}/clear` | Снять назначение |
| GET | `/api/admin/tasks` | Все задачи (админ) |
| POST | `/api/admin/tasks/create` | Создать задачу |

## 🔐 Аутентификация

Используется JWT (Bearer token). После регистрации/входа:

```
Authorization: Bearer <token>
```

## 🌐 WebSocket

Подключение к лидерборду в реальном времени:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/leaderboard/');
```

## 🗄 База данных

По умолчанию используется SQLite. Для PostgreSQL:

```
DATABASE_URL=postgresql://user:password@localhost:5432/sql_battle
```
