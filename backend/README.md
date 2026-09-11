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
├── templates/           # Django Admin шаблоны
│   └── admin/
│       └── api/
│           ├── taskassignment/
│           │   └── bulk_assign.html
│           └── usergroup/
│               ├── create.html
│               ├── edit.html
│               └── assign.html
└── api/
    ├── models.py        # User, Task, Submission, TaskAssignment, UserGroup
    ├── serializers.py   # Оба формата: camelCase + snake_case
    ├── views.py         # Принимает time_spent
    ├── urls.py
    ├── consumers.py     # Возвращает total_time_spent
    ├── middleware.py    # QueryAuthMiddleware для WebSocket
    ├── routing.py
    ├── utils.py
    ├── permissions.py
    ├── admin.py         # Кастомные Django Admin views
    ├── forms.py         # Формы для Django Admin
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

### Пользователь
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/user/assigned-tasks` | Все назначенные задачи (массив) |
| GET | `/user/assigned-task` | Первая назначенная задача (совместимость) |

### Админка — Пользователи
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/admin/users` | `{ assignedTaskId, assignedTaskIds }` |
| POST | `/admin/users/{id}/assign` | Назначить задачу(и): `{taskId}` или `{task_ids: [1,2,3]}` |
| POST | `/admin/users/{id}/clear` | Снять: `{taskId}` или все |

### Админка — Группы
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/admin/groups` | Список всех групп |
| POST | `/admin/groups/create` | Создать группу: `{name, description, user_ids}` |
| GET | `/admin/groups/{id}` | Детали группы |
| PUT | `/admin/groups/{id}` | Обновить группу |
| DELETE | `/admin/groups/{id}` | Удалить группу |
| POST | `/admin/groups/{id}/assign` | Назначить задачи группе: `{task_ids: [1,2,3]}` |
| POST | `/admin/groups/{id}/clear` | Снять назначения группы |

### Админка — Задачи и настройки
| Метод | URL | Описание |
|-------|-----|----------|
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

## 📋 Примеры использования

### Массовое назначение задач пользователю

```bash
# Назначить одну задачу
POST /admin/users/1/assign
{"taskId": 3}

# Назначить несколько задач сразу
POST /admin/users/1/assign
{"task_ids": [1, 2, 3, 5]}
```

**Автоматические даты при назначении:**
- `started_at`: текущее время + 1 минута
- `completed_at`: текущее время + 24 часа

### Работа с группами

```bash
# Создать группу
POST /admin/groups/create
{
  "name": "Команда А",
  "description": "Первая команда участников",
  "user_ids": [1, 2, 3, 4]
}

# Назначить задачи всей группе
POST /admin/groups/1/assign
{"task_ids": [1, 2, 3]}

# Снять все назначения у группы
POST /admin/groups/1/clear
{}

# Снять конкретные задачи у группы
POST /admin/groups/1/clear
{"task_ids": [1, 2]}
```

### Получение назначенных задач

```bash
# Получить все назначенные задачи (массив)
GET /user/assigned-tasks
Response: [
  {
    "id": 1,
    "title": "Задача 1",
    "difficulty": "easy",
    "points": 100,
    "solved": false,
    "assigned_at": "2026-09-10T10:00:00Z"
  },
  ...
]

# Получить первую задачу (для совместимости)
GET /user/assigned-task
Response: {
  "id": 1,
  "title": "Задача 1",
  "difficulty": "easy",
  "points": 100
}
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

## 🎛️ Django Admin — Массовое назначение задач

### Доступ к Django Admin

```bash
# Создайте суперпользователя (если ещё не создан)
python manage.py create_admin --username admin --password admin123

# Запустите сервер
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application

# Откройте http://localhost:8000/admin/
```

### Функционал Django Admin

#### 1. Массовое назначение задач (TaskAssignments)

Перейдите в **Task assignments** → нажмите кнопку **"Массовое назначение задач"** вверху страницы.

**Возможности:**
- ✅ Выберите тип назначения: **пользователю** или **группе**
- ✅ Выберите одного или нескольких пользователей
- ✅ Выберите одну или несколько задач
- ✅ Все выбранные задачи будут назначены всем выбранным пользователям

**Пример использования:**
1. Выберите "Пользователю"
2. Отметьте 5 пользователей чекбоксами
3. Отметьте 3 задачи чекбоксами
4. Нажмите "Назначить задачи"
5. Результат: 15 назначений (5 пользователей × 3 задачи)

#### 2. Управление группами (User Groups)

Перейдите в **User groups** для управления группами пользователей.

**Действия:**
- **Добавить User group** — создать новую группу
- **Изменить** — редактировать группу (название, описание, участники)
- **Назначить задачи** — назначить задачи всем участникам группы

**Пример использования:**
1. Создайте группу "Команда А"
2. Добавьте 10 пользователей в группу
3. Нажмите "Назначить задачи" рядом с группой
4. Выберите 5 задач
5. Результат: 50 назначений (10 пользователей × 5 задач)

#### 3. Просмотр назначений

В разделе **Task assignments** можно:
- Фильтровать по пользователю или задаче
- Видеть статус назначения (назначено, начато, завершено)
- Удалять отдельные назначения

### Скриншоты функционала

**Массовое назначение:**
```
┌─────────────────────────────────────────┐
│ Массовое назначение задач               │
├─────────────────────────────────────────┤
│ 1. Выберите тип назначения              │
│    ○ Пользователю                       │
│    ○ Группе пользователей               │
│                                         │
│ 2. Выберите пользователей               │
│    ☐ Иван Петров                        │
│    ☐ Мария Сидорова                     │
│    ☐ Дмитрий Козлов                     │
│                                         │
│ 3. Выберите задачи                      │
│    ☐ Найди активных хакеров (easy)      │
│    ☐ Анализ заказов (hard)              │
│    ☐ Топ-10 заказов (medium)            │
│                                         │
│ [Назначить задачи]  [Отмена]            │
└─────────────────────────────────────────┘
```

**Управление группами:**
```
┌─────────────────────────────────────────┐
│ User groups                             │
├─────────────────────────────────────────┤
│ [Добавить User group]                   │
│                                         │
│ Название    │ Пользователи │ Действия   │
│─────────────┼──────────────┼────────────│
│ Команда А   │ 10           │ Изменить   │
│             │              │ Назначить  │
│─────────────┼──────────────┼────────────│
│ Команда Б   │ 8            │ Изменить   │
│             │              │ Назначить  │
└─────────────────────────────────────────┘
```
