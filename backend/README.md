# SQL Battle Backend (Django)

Бэкенд для платформы SQL-баттлов на Django REST Framework.  
**Полностью совместим с фронтендом** [Mptmon/sql-battle](https://github.com/Mptmon/sql-battle).

## ✅ Соответствие фронтенду

Все эндпоинты, форматы данных и camelCase/snake_case согласованы с `lib/api.ts` фронтенда:

| Фронтенд ожидает | Бэкенд возвращает | Статус |
|---|---|---|
| `{ token, user }` | `{ token, user }` | ✅ |
| `totalPoints` (camelCase) | `totalPoints` | ✅ |
| `solvedTasks` (camelCase) | `solvedTasks` | ✅ |
| `expectedResult` (camelCase) | `expectedResult` | ✅ |
| `{ taskId }` в assign | Принимает `taskId` | ✅ |
| `assignedTaskId` в admin/users | `assignedTaskId` | ✅ |
| `GET/PUT /admin/settings` | Реализовано | ✅ |
| `ws://...:8000/ws/leaderboard` | `/ws/leaderboard/` | ✅ |

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash

git clone https://github.com/ShildJR/backend_sql_battle_DRF

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
Для теста редактировать не требуется
```

### 3. Миграции и запуск

```bash
python manage.py migrate
python manage.py loaddata api/fixtures/tasks.json  # Загрузить примеры задач
python manage.py create_admin --username admin --password admin123
```

### 4. Запуск сервера (ВАЖНО: нужен ASGI для WebSocket!)

**Для разработки** (с автоматической перезагрузкой):
```bash
# Вариант 1: Через daphne (рекомендуется)
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application

# Вариант 2: Через uvicorn
uvicorn sql_battle.asgi:application --host 0.0.0.0 --port 8000 --reload

# Вариант 3: Через Django runserver (только если установлен channels)
python manage.py runserver 0.0.0.0:8000
```

**Для продакшена**:
```bash
# HTTP + WebSocket через daphne
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application

# Или через uvicorn + gunicorn
gunicorn sql_battle.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

⚠️ **Внимание**: Обычный `python manage.py runserver` **НЕ поддерживает WebSocket** без установленного `channels`. Если WebSocket не работает, используйте `daphne` или `uvicorn`.

## 📁 Структура проекта

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── sql_battle/          # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── api/                 # Основное приложение
    ├── models.py        # User, Task, Submission, TaskAssignment
    ├── serializers.py   # DRF сериализаторы (camelCase)
    ├── views.py         # Все API-представления
    ├── urls.py          # Маршруты API
    ├── consumers.py     # WebSocket для лидерборда
    ├── routing.py       # WebSocket маршруты
    ├── utils.py         # SQL Sandbox + сравнение результатов
    ├── permissions.py   # IsAdmin
    ├── admin.py         # Django Admin
    ├── fixtures/        # Примеры задач
    └── management/      # Команда create_admin
```

## 🔌 API Endpoints

### Аутентификация
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register` | Регистрация → `{ token, user }` |
| POST | `/api/auth/login` | Вход → `{ token, user }` |

### Профиль
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/profile` | `{ totalPoints, solvedTasks, rank }` |

### Задачи
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/tasks` | Список с полем `status` |
| GET | `/api/tasks/{id}` | `{ expectedResult }` (camelCase) |
| POST | `/api/tasks/{id}/execute` | Выполнить SQL (sandbox) |
| POST | `/api/tasks/{id}/submit` | Проверка решения |

### Лидерборд
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/leaderboard` | `{ totalPoints, solvedTasks, avgTime }` |
| WS | `/ws/leaderboard/` | Реалтайм обновления |

### Админка
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/admin/users` | `{ assignedTaskId }` |
| POST | `/api/admin/users/{id}/assign` | `{ taskId }` (camelCase) |
| POST | `/api/admin/users/{id}/clear` | Снять назначение |
| GET | `/api/user/assigned-task` | Для лобби |
| GET | `/api/admin/tasks` | Все задачи |
| POST | `/api/admin/tasks` | Создать задачу |
| GET | `/api/admin/settings` | Настройки баттла |
| PUT | `/api/admin/settings` | Обновить настройки |

## 🔐 Аутентификация

JWT Bearer token. Фронтенд сохраняет токен и отправляет:
```
Authorization: Bearer <token>
```

Ответы auth endpoints:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "ivan.petrov",
    "email": "ivan@cdek.digital",
    "rating": 0,
    "totalPoints": 0,
    "role": "participant"
  }
}
```

## 🛡️ Безопасность

- **SQL Sandbox** — SQLite временная БД для каждого запроса
- **Только SELECT** — запрет INSERT/UPDATE/DELETE/DROP/ALTER/CREATE
- **Таймаут** — 3 секунды
- **Сравнение результатов** — не текста запроса

## 🐳 Docker

```bash
docker-compose up -d
```
