# Быстрый старт SQL Battle Backend

## Установка и запуск

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Создание администратора

```bash
python manage.py create_admin
```

Вам будет предложено ввести:
- Имя пользователя
- Email (опционально)
- Пароль

### 4. Загрузка тестовых задач (опционально)

```bash
python manage.py loaddata api/fixtures/tasks.json
```

### 5. Запуск сервера разработки

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: `http://localhost:8000`

## Доступ к API

- **API**: `http://localhost:8000/api/`
- **Django Admin**: `http://localhost:8000/django-admin/`
- **WebSocket**: `ws://localhost:8000/ws/leaderboard/`

## Основные эндпоинты

### Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход

### Задачи
- `GET /api/tasks` - Список задач
- `GET /api/tasks/{id}` - Детали задачи
- `POST /api/tasks/{id}/execute` - Выполнить SQL запрос
- `POST /api/tasks/{id}/submit` - Отправить решение

### Профиль
- `GET /api/profile` - Профиль пользователя
- `GET /api/profile/history` - История решений

### Лидерборд
- `GET /api/leaderboard` - Таблица лидеров
- `WebSocket /ws/leaderboard/` - Обновления в реальном времени

### Администрирование
- `GET /api/admin/users` - Список пользователей
- `POST /api/admin/users/{id}/assign` - Назначить задачу
- `GET /api/admin/tasks` - Все задачи
- `POST /api/admin/tasks` - Создать задачу
- `GET /api/admin/settings` - Настройки
- `PUT /api/admin/settings` - Обновить настройки

## Использование Django Admin

1. Перейдите на `http://localhost:8000/django-admin/`
2. Войдите с учетными данными администратора
3. Используйте встроенные инструменты для:
   - Массового назначения задач пользователям
   - Управления группами пользователей
   - Просмотра и редактирования задач
   - Управления настройками

## Дополнительная документация

- [README.md](README.md) - Основная документация
- [COMPLIANCE_REPORT.md](COMPLIANCE_REPORT.md) - Отчет о соответствии фронтенду
- [DJANGO_ADMIN_GUIDE.md](DJANGO_ADMIN_GUIDE.md) - Руководство по Django Admin
