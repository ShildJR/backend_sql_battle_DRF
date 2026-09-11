# SQL Battle Backend (Django)

Бэкенд для платформы SQL-баттлов на Django REST Framework.  
**Полностью совместим с фронтендом** [Mptmon/sql-battle](https://github.com/Mptmon/sql-battle).

## ✅ Соответствие фронтенду

Все эндпоинты, форматы данных и camelCase/snake_case согласованы с `lib/api.ts` фронтенда:

| Фронтенд ожидает | Бэкенд возвращает | Статус |
|---|---|---|
| `{ token, user }` | `{ token, user }` | ✅ |
| `totalPoints` / `total_points` | Оба формата | ✅ |
| `solvedTasks` / `solved_tasks` | Оба формата | ✅ |
| `expectedResult` (camelCase) | `expectedResult` | ✅ |
| `{ taskId }` в assign | Принимает `taskId` | ✅ |
| `assignedTaskId` в admin/users | `assignedTaskId` | ✅ |
| `total_time_spent` в лидерборде | `total_time_spent` + `totalTimeSpent` | ✅ |
| `time_spent` в submit | Принимает `time_spent` | ✅ |
| `GET /admin/settings` | Реализовано | ✅ |
| `ws://...:8000/ws/leaderboard?token=...` | `/ws/leaderboard/?token=...` | ✅ |
| URL без `/api` префикса | Убран префикс | ✅ |

## 🆕 Последние изменения

### 1. Убран префикс `/api`
Фронтенд теперь обращается напрямую: `http://localhost:8000/tasks` вместо `http://localhost:8000/api/tasks`

### 2. Добавлен `time_spent` в submit
Фронтенд отправляет время, потраченное на решение:
```json
POST /tasks/{id}/submit
{
  "query": "SELECT ...",
  "time_spent": 45.5  // секунды
}
```

### 3. Лидерборд возвращает `total_time_spent`
Вместо `avgTime` теперь возвращается общее время:
```json
{
  "rank": 1,
  "username": "...",
  "totalPoints": 1250,
  "solvedTasks": 8,
  "total_time_spent": 120.5,
  "totalTimeSpent": 120.5,
  "avgTime": 15.06
}
```

### 4. Профиль возвращает оба формата
```json
{
  "id": 1,
  "username": "ivan",
  "totalPoints": 450,
  "total_points": 450,
  "solvedTasks": [1, 2, 5],
  "solved_tasks": [1, 2, 5],
  "rank": 3,
  "role": "participant"
}
```

### 5. `/tasks` доступен без авторизации
Список задач теперь публичный.

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
```

### 3. Миграции и данные

```bash
python manage.py migrate
python manage.py loaddata api/fixtures/tasks.json
python manage.py create_admin --username admin --password admin123
```

### 4. Запуск сервера (ВАЖНО: нужен ASGI для WebSocket!)

```bash
# ✅ ПРАВИЛЬНО — через ASGI-сервер:
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application

# Или:
uvicorn sql_battle.asgi:application --host 0.0.0.0 --port 8000 --reload

# ❌ НЕ РАБОТАЕТ для WebSocket:
python manage.py runserver 0.0.0.0:8000
```

## 📁 Структура проекта

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── sql_battle/
│   ├── settings.py
│   ├── urls.py          # Убран префикс 'api/'
│   ├── wsgi.py
│   └── asgi.py          # С QueryAuthMiddleware
└── api/
    ├── models.py
    ├── serializers.py   # Оба формата: camelCase + snake_case
    ├── views.py         # Принимает time_spent
    ├── urls.py
    ├── consumers.py     # Возвращает total_time_spent
    ├── middleware.py    # QueryAuthMiddleware для WebSocket
    ├── routing.py
    ├── utils.py
    ├── permissions.py
    ├── admin.py
    ├── fixtures/
    └── management/
```

## 🔌 API Endpoints

### Аутентификация
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/auth/register` | Регистрация → `{ token, user }` |
| POST | `/auth/login` | Вход → `{ token, user }` |

### Профиль
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/profile` | `{ totalPoints, total_points, solvedTasks, solved_tasks, rank }` |
| GET | `/profile/history` | История решений |

### Задачи
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/tasks` | Список (без авторизации) |
| GET | `/tasks/{id}` | Детали (с авторизацией) |
| POST | `/tasks/{id}/execute` | Выполнить SQL |
| POST | `/tasks/{id}/submit` | Проверка (принимает `time_spent`) |

### Лидерборд
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/leaderboard` | `{ total_time_spent, totalTimeSpent, avgTime }` |
| WS | `/ws/leaderboard/?token=...` | Реалтайм обновления |

### Админка
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/admin/users` | `{ assignedTaskId }` |
| POST | `/admin/users/{id}/assign` | `{ taskId }` |
| POST | `/admin/users/{id}/clear` | Снять назначение |
| GET | `/user/assigned-task` | Для лобби |
| GET | `/admin/tasks` | Все задачи |
| POST | `/admin/tasks` | Создать задачу |
| GET | `/admin/settings` | Настройки баттла |
| PUT | `/admin/settings` | Обновить настройки |

## 🔐 Аутентификация

JWT Bearer token:
```
Authorization: Bearer <token>
```

WebSocket — токен в query-параметре:
```
ws://localhost:8000/ws/leaderboard?token=<jwt_token>
```

## 🛡️ Безопасность

- **SQL Sandbox** — SQLite временная БД
- **Только SELECT** — запрет INSERT/UPDATE/DELETE/DROP/ALTER/CREATE
- **Таймаут** — 3 секунды
- **Сравнение результатов** — не текста запроса

## 🐳 Docker

```bash
docker-compose up -d
```
