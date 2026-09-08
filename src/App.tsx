import { useState } from 'react'

type Tab = 'overview' | 'endpoints' | 'models' | 'setup' | 'websocket'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'overview', label: 'Обзор', icon: '📋' },
    { id: 'endpoints', label: 'API Endpoints', icon: '🔌' },
    { id: 'models', label: 'Модели', icon: '🗄' },
    { id: 'setup', label: 'Запуск', icon: '🚀' },
    { id: 'websocket', label: 'WebSocket', icon: '⚡' },
  ]

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center font-bold text-lg">
              ⚔️
            </div>
            <div>
              <h1 className="text-xl font-bold">SQL Battle Backend</h1>
              <p className="text-xs text-gray-400">Django REST Framework • cdek_digital</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-green-900/50 text-green-400 text-xs rounded-full border border-green-800">
              Django 4.2+
            </span>
            <span className="px-2 py-1 bg-blue-900/50 text-blue-400 text-xs rounded-full border border-blue-800">
              DRF
            </span>
            <span className="px-2 py-1 bg-purple-900/50 text-purple-400 text-xs rounded-full border border-purple-800">
              Channels
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Tabs */}
        <nav className="flex gap-1 mb-8 bg-gray-900 p-1 rounded-xl border border-gray-800 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-gray-800 text-white shadow-lg'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Content */}
        <main>
          {activeTab === 'overview' && <OverviewTab />}
          {activeTab === 'endpoints' && <EndpointsTab copyCode={copyCode} copiedCode={copiedCode} />}
          {activeTab === 'models' && <ModelsTab />}
          {activeTab === 'setup' && <SetupTab copyCode={copyCode} copiedCode={copiedCode} />}
          {activeTab === 'websocket' && <WebSocketTab copyCode={copyCode} copiedCode={copiedCode} />}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-16 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>SQL Battle Backend • Django REST Framework • Для платформы cdek_digital</p>
        </div>
      </footer>
    </div>
  )
}

function CodeBlock({ code, id, copyCode, copiedCode, language = 'bash' }: { 
  code: string; 
  id: string; 
  copyCode: (code: string, id: string) => void;
  copiedCode: string | null;
  language?: string;
}) {
  return (
    <div className="relative group">
      <div className="absolute top-2 right-2 flex items-center gap-2">
        <span className="text-xs text-gray-500">{language}</span>
        <button
          onClick={() => copyCode(code, id)}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition-colors opacity-0 group-hover:opacity-100"
        >
          {copiedCode === id ? '✓ Скопировано' : 'Копировать'}
        </button>
      </div>
      <pre className="bg-gray-900 border border-gray-800 rounded-lg p-4 overflow-x-auto text-sm">
        <code className="text-gray-300">{code}</code>
      </pre>
    </div>
  )
}

function OverviewTab() {
  const architecture = `┌─────────────────────┐
│     Frontend        │  Next.js 16 + React + TypeScript
│   (отдельный репо)   │  Tailwind CSS + shadcn/ui
└──────────┬──────────┘
           │ HTTP / WebSocket
           ▼
┌─────────────────────┐
│     Backend         │  Django 4.2 + DRF
│   (этот проект)     │  Channels (WebSocket)
│                     │  SQLite / PostgreSQL
└─────────────────────┘`

  const projectStructure = `backend/
├── manage.py                    # Управление проектом
├── requirements.txt             # Зависимости Python
├── .env.example                 # Пример конфигурации
├── sql_battle/                  # Настройки Django
│   ├── __init__.py
│   ├── settings.py              # Основные настройки
│   ├── urls.py                  # Корневые URL
│   ├── wsgi.py                  # WSGI для продакшена
│   └── asgi.py                  # ASGI для WebSocket
└── api/                         # Основное приложение
    ├── models.py                # Модели БД (User, Task, Submission, TaskAssignment)
    ├── serializers.py           # DRF сериализаторы
    ├── views.py                 # API-представления
    ├── urls.py                  # Маршруты API
    ├── consumers.py             # WebSocket consumer (лидерборд)
    ├── routing.py               # WebSocket маршруты
    ├── utils.py                 # SQL Sandbox + валидация
    ├── permissions.py           # Кастомные разрешения
    ├── admin.py                 # Django Admin
    ├── management/commands/     # Кастомные команды
    │   └── create_admin.py      # Создание админа
    ├── fixtures/
    │   └── tasks.json           # Примеры задач
    └── migrations/              # Миграции БД`

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-2">🎯 SQL Battle Backend</h2>
        <p className="text-gray-300">
          Бэкенд для платформы проведения SQL-соревнований. Реализует полный API-контракт 
          для фронтенда на Next.js с поддержкой JWT-аутентификации, WebSocket-лидерборда 
          и безопасного выполнения SQL-запросов в sandbox.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>🏗</span> Архитектура
          </h3>
          <pre className="text-sm text-gray-300 whitespace-pre">{architecture}</pre>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📁</span> Структура проекта
          </h3>
          <pre className="text-xs text-gray-300 whitespace-pre overflow-x-auto">{projectStructure}</pre>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <FeatureCard
          icon="🔐"
          title="JWT Аутентификация"
          description="Bearer-токены через djangorestframework-simplejwt. Защита всех эндпоинтов кроме /auth/*"
        />
        <FeatureCard
          icon="🛡️"
          title="SQL Sandbox"
          description="Безопасное выполнение SQL через SQLite. Запрет INSERT/UPDATE/DELETE/DROP. Таймаут 3 сек."
        />
        <FeatureCard
          icon="⚡"
          title="WebSocket"
          description="Реалтайм-обновления лидерборда через Django Channels. InMemoryChannelLayer."
        />
        <FeatureCard
          icon="👥"
          title="Роли"
          description="Участник и Администратор. Админы управляют задачами и назначают их пользователям."
        />
        <FeatureCard
          icon="📊"
          title="Лидерборд"
          description="Рейтинг по баллам, количество решённых задач, среднее время решения."
        />
        <FeatureCard
          icon="🗄"
          title="БД"
          description="SQLite для разработки, PostgreSQL для продакшена. Авто-миграции Django."
        />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">📦 Зависимости</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { name: 'Django', version: '4.2+', desc: 'Веб-фреймворк' },
            { name: 'DRF', version: '3.14+', desc: 'REST API' },
            { name: 'simplejwt', version: '5.3+', desc: 'JWT-аутентификация' },
            { name: 'django-cors-headers', version: '4.3+', desc: 'CORS' },
            { name: 'channels', version: '4.0+', desc: 'WebSocket' },
            { name: 'psycopg2-binary', version: '2.9+', desc: 'PostgreSQL драйвер' },
          ].map((dep) => (
            <div key={dep.name} className="flex items-center gap-3 p-2 bg-gray-800/50 rounded-lg">
              <span className="px-2 py-0.5 bg-blue-900/50 text-blue-400 text-xs rounded font-mono">
                {dep.version}
              </span>
              <div>
                <span className="text-sm font-medium">{dep.name}</span>
                <span className="text-xs text-gray-500 ml-2">— {dep.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors">
      <div className="text-2xl mb-2">{icon}</div>
      <h4 className="font-semibold mb-1">{title}</h4>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  )
}

function EndpointsTab({ copyCode, copiedCode }: { copyCode: (code: string, id: string) => void; copiedCode: string | null }) {
  const endpoints = [
    {
      section: '🔐 Аутентификация',
      items: [
        { method: 'POST', path: '/api/auth/register', desc: 'Регистрация', auth: false,
          body: '{"username": "ivan", "email": "ivan@mail.ru", "password": "pass123"}',
          response: '{"token": "eyJ...", "user": {"id": 1, "username": "ivan", ...}}' },
        { method: 'POST', path: '/api/auth/login', desc: 'Вход', auth: false,
          body: '{"username": "ivan", "password": "pass123"}',
          response: '{"token": "eyJ...", "user": {...}}' },
      ]
    },
    {
      section: '👤 Профиль',
      items: [
        { method: 'GET', path: '/api/profile', desc: 'Данные пользователя', auth: true,
          response: '{"id": 1, "username": "ivan", "rating": 1250, "total_points": 450, "rank": 3, "solved_tasks": [1, 2], "role": "participant"}' },
      ]
    },
    {
      section: '🎮 Задачи',
      items: [
        { method: 'GET', path: '/api/tasks', desc: 'Список задач', auth: true,
          response: '[{"id": 1, "title": "...", "difficulty": "easy", "points": 100, "status": "unsolved"}]' },
        { method: 'GET', path: '/api/tasks/{id}', desc: 'Детали задачи', auth: true,
          response: '{"id": 1, "title": "...", "description": "...", "schema": "...", "tables": [...]}' },
        { method: 'POST', path: '/api/tasks/{id}/execute', desc: 'Выполнить запрос (Run)', auth: true,
          body: '{"query": "SELECT name FROM users WHERE status = \'active\'"}',
          response: '{"status": "success", "data": [...], "execution_time": 0.045}' },
        { method: 'POST', path: '/api/tasks/{id}/submit', desc: 'Отправить решение', auth: true,
          body: '{"query": "SELECT city, COUNT(*) as user_count FROM users GROUP BY city"}',
          response: '{"is_correct": true, "points_earned": 100, "new_total_points": 550, "expected_result": [...]}' },
      ]
    },
    {
      section: '🏆 Лидерборд',
      items: [
        { method: 'GET', path: '/api/leaderboard', desc: 'Топ участников', auth: false,
          response: '[{"rank": 1, "username": "...", "total_points": 1250, "solved_tasks": 8, "avg_time": 0.45, "avatar": "АС"}]' },
      ]
    },
    {
      section: '👥 Админка',
      items: [
        { method: 'GET', path: '/api/admin/users', desc: 'Все пользователи', auth: true, admin: true,
          response: '[{"id": 1, "username": "ivan", "total_points": 450, "assigned_task_id": 3}]' },
        { method: 'POST', path: '/api/admin/users/{id}/assign', desc: 'Назначить задачу', auth: true, admin: true,
          body: '{"task_id": 3}',
          response: '{"success": true, "message": "Задача назначена"}' },
        { method: 'POST', path: '/api/admin/users/{id}/clear', desc: 'Снять назначение', auth: true, admin: true,
          response: '{"success": true, "message": "Назначение снято"}' },
        { method: 'GET', path: '/api/user/assigned-task', desc: 'Назначенная задача', auth: true,
          response: '{"id": 3, "title": "...", "difficulty": "hard", "points": 500}' },
        { method: 'GET', path: '/api/admin/tasks', desc: 'Все задачи (админ)', auth: true, admin: true,
          response: '[{"id": 1, "title": "...", "expected_result": [...]}]' },
        { method: 'POST', path: '/api/admin/tasks/create', desc: 'Создать задачу', auth: true, admin: true,
          body: '{"title": "...", "description": "...", "difficulty": "medium", "points": 250, "schema": "...", "tables": [...], "expected_result": [...]}',
          response: '{"id": 10, "title": "...", "success": true}' },
      ]
    },
  ]

  return (
    <div className="space-y-8">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-sm text-gray-400">
          <span className="text-yellow-400 font-mono">Base URL:</span>{' '}
          <code className="text-green-400">http://localhost:8000</code>
          {' • '}
          <span className="text-yellow-400 font-mono">Auth:</span>{' '}
          <code className="text-green-400">Authorization: Bearer {'<token>'}</code>
        </p>
      </div>

      {endpoints.map((section) => (
        <div key={section.section} className="space-y-3">
          <h3 className="text-lg font-semibold">{section.section}</h3>
          <div className="space-y-2">
            {section.items.map((ep, idx) => (
              <EndpointCard 
                key={idx} 
                endpoint={ep} 
                copyCode={copyCode} 
                copiedCode={copiedCode} 
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function EndpointCard({ endpoint, copyCode, copiedCode }: { 
  endpoint: any; 
  copyCode: (code: string, id: string) => void;
  copiedCode: string | null;
}) {
  const [expanded, setExpanded] = useState(false)
  const methodColors: Record<string, string> = {
    GET: 'bg-green-900/50 text-green-400 border-green-800',
    POST: 'bg-blue-900/50 text-blue-400 border-blue-800',
    PUT: 'bg-yellow-900/50 text-yellow-400 border-yellow-800',
    DELETE: 'bg-red-900/50 text-red-400 border-red-800',
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-3 hover:bg-gray-800/50 transition-colors text-left"
      >
        <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded border ${methodColors[endpoint.method]}`}>
          {endpoint.method}
        </span>
        <code className="text-sm font-mono text-gray-300 flex-1">{endpoint.path}</code>
        <span className="text-sm text-gray-400">{endpoint.desc}</span>
        {endpoint.admin && <span className="px-1.5 py-0.5 bg-red-900/30 text-red-400 text-xs rounded">admin</span>}
        {!endpoint.auth && <span className="px-1.5 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">public</span>}
        <span className="text-gray-500">{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <div className="border-t border-gray-800 p-4 space-y-3">
          {endpoint.body && (
            <div>
              <p className="text-xs text-gray-500 mb-1">Request Body:</p>
              <CodeBlock code={endpoint.body} id={`body-${endpoint.path}`} copyCode={copyCode} copiedCode={copiedCode} language="json" />
            </div>
          )}
          {endpoint.response && (
            <div>
              <p className="text-xs text-gray-500 mb-1">Response:</p>
              <CodeBlock code={endpoint.response} id={`resp-${endpoint.path}`} copyCode={copyCode} copiedCode={copiedCode} language="json" />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function ModelsTab() {
  const models = [
    {
      name: 'User',
      desc: 'Пользователь (наследует AbstractUser)',
      fields: [
        { name: 'id', type: 'AutoField', desc: 'Primary Key' },
        { name: 'username', type: 'CharField(50)', desc: 'Уникальное имя' },
        { name: 'email', type: 'EmailField', desc: 'Email' },
        { name: 'password', type: 'CharField', desc: 'Хеш пароля' },
        { name: 'rating', type: 'IntegerField', desc: 'Рейтинг (default: 0)' },
        { name: 'total_points', type: 'IntegerField', desc: 'Всего баллов (default: 0)' },
        { name: 'role', type: 'CharField(20)', desc: 'participant / admin' },
        { name: 'created_at', type: 'DateTimeField', desc: 'Дата создания' },
      ]
    },
    {
      name: 'Task',
      desc: 'Задача для SQL-баттла',
      fields: [
        { name: 'id', type: 'AutoField', desc: 'Primary Key' },
        { name: 'title', type: 'CharField(200)', desc: 'Название задачи' },
        { name: 'description', type: 'TextField', desc: 'Описание' },
        { name: 'difficulty', type: 'CharField(20)', desc: 'easy / medium / hard' },
        { name: 'points', type: 'IntegerField', desc: 'Баллы за решение' },
        { name: 'schema', type: 'TextField', desc: 'DDL для создания таблиц' },
        { name: 'tables', type: 'JSONField', desc: 'Структура таблиц + примеры' },
        { name: 'expected_result', type: 'JSONField', desc: 'Эталонный результат' },
        { name: 'created_at', type: 'DateTimeField', desc: 'Дата создания' },
      ]
    },
    {
      name: 'Submission',
      desc: 'Попытка решения задачи',
      fields: [
        { name: 'id', type: 'AutoField', desc: 'Primary Key' },
        { name: 'user', type: 'ForeignKey(User)', desc: 'Автор решения' },
        { name: 'task', type: 'ForeignKey(Task)', desc: 'Задача' },
        { name: 'query', type: 'TextField', desc: 'SQL-запрос' },
        { name: 'is_correct', type: 'BooleanField', desc: 'Правильно ли' },
        { name: 'points_earned', type: 'IntegerField', desc: 'Заработанные баллы' },
        { name: 'execution_time_ms', type: 'IntegerField', desc: 'Время выполнения (мс)' },
        { name: 'created_at', type: 'DateTimeField', desc: 'Дата отправки' },
      ]
    },
    {
      name: 'TaskAssignment',
      desc: 'Назначение задачи участнику',
      fields: [
        { name: 'id', type: 'AutoField', desc: 'Primary Key' },
        { name: 'user', type: 'OneToOneField(User)', desc: 'Пользователь (уникально)' },
        { name: 'task', type: 'ForeignKey(Task)', desc: 'Назначенная задача' },
        { name: 'assigned_at', type: 'DateTimeField', desc: 'Когда назначена' },
        { name: 'started_at', type: 'DateTimeField', desc: 'Когда начата' },
        { name: 'completed_at', type: 'DateTimeField', desc: 'Когда завершена' },
      ]
    },
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-sm text-gray-400">
          Модели определены в <code className="text-green-400">api/models.py</code>. 
          AUTH_USER_MODEL = 'api.User'. Миграции: <code className="text-green-400">python manage.py migrate</code>
        </p>
      </div>

      {models.map((model) => (
        <div key={model.name} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-800/30">
            <h3 className="font-bold text-lg">{model.name}</h3>
            <p className="text-sm text-gray-400">{model.desc}</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-800">
                  <th className="px-4 py-2">Поле</th>
                  <th className="px-4 py-2">Тип</th>
                  <th className="px-4 py-2">Описание</th>
                </tr>
              </thead>
              <tbody>
                {model.fields.map((field) => (
                  <tr key={field.name} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="px-4 py-2 font-mono text-blue-400">{field.name}</td>
                    <td className="px-4 py-2 font-mono text-purple-400 text-xs">{field.type}</td>
                    <td className="px-4 py-2 text-gray-300">{field.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}

function SetupTab({ copyCode, copiedCode }: { copyCode: (code: string, id: string) => void; copiedCode: string | null }) {
  const steps = [
    {
      title: '1. Клонирование и виртуальное окружение',
      code: `cd backend
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\\Scripts\\activate`
    },
    {
      title: '2. Установка зависимостей',
      code: 'pip install -r requirements.txt'
    },
    {
      title: '3. Настройка окружения',
      code: `cp .env.example .env
# Отредактируйте .env при необходимости:
# SECRET_KEY=your-secret-key
# DEBUG=True
# DATABASE_URL=sqlite:///db.sqlite3`
    },
    {
      title: '4. Миграции базы данных',
      code: `python manage.py migrate`
    },
    {
      title: '5. Загрузка примеров задач',
      code: 'python manage.py loaddata api/fixtures/tasks.json'
    },
    {
      title: '6. Создание админ-пользователя',
      code: `# Вариант 1: Кастомная команда
python manage.py create_admin --username admin --password admin123

# Вариант 2: Через Django shell
python manage.py shell
>>> from api.models import User
>>> admin = User.objects.create_superuser('admin', 'admin@mail.ru', 'admin123')
>>> admin.role = 'admin'
>>> admin.save()`
    },
    {
      title: '7. Запуск сервера',
      code: `# Разработка
python manage.py runserver 0.0.0.0:8000

# Продакшен (с gunicorn + daphne для WebSocket)
gunicorn sql_battle.wsgi:application --bind 0.0.0.0:8000
daphne -b 0.0.0.0 -p 8001 sql_battle.asgi:application`
    },
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-2">🚀 Инструкция по запуску</h2>
        <p className="text-gray-300">
          Следуйте шагам ниже для запуска бэкенда локально. По умолчанию используется SQLite.
        </p>
      </div>

      {steps.map((step, idx) => (
        <div key={idx} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-semibold mb-3">{step.title}</h3>
          <CodeBlock code={step.code} id={`setup-${idx}`} copyCode={copyCode} copiedCode={copiedCode} />
        </div>
      ))}

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="font-semibold mb-3">🐘 PostgreSQL (опционально)</h3>
        <p className="text-sm text-gray-400 mb-3">Для продакшена рекомендуется PostgreSQL:</p>
        <CodeBlock 
          code={`# .env
DATABASE_URL=postgresql://user:password@localhost:5432/sql_battle

# Или создайте БД:
# CREATE DATABASE sql_battle;
# CREATE USER sql_user WITH PASSWORD 'password';
# GRANT ALL PRIVILEGES ON DATABASE sql_battle TO sql_user;`}
          id="postgres-config"
          copyCode={copyCode}
          copiedCode={copiedCode}
        />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="font-semibold mb-3">✅ Проверка работы</h3>
        <div className="space-y-2 text-sm">
          <p className="text-gray-300">После запуска проверьте:</p>
          <ul className="space-y-1 text-gray-400 ml-4">
            <li>• <code className="text-green-400">http://localhost:8000/admin/</code> — Django Admin</li>
            <li>• <code className="text-green-400">POST /api/auth/register</code> — регистрация</li>
            <li>• <code className="text-green-400">GET /api/leaderboard</code> — лидерборд</li>
            <li>• <code className="text-green-400">GET /api/tasks</code> — список задач (с токеном)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function WebSocketTab({ copyCode, copiedCode }: { copyCode: (code: string, id: string) => void; copiedCode: string | null }) {
  const clientCode = `// Подключение к WebSocket лидерборда
const ws = new WebSocket('ws://localhost:8000/ws/leaderboard/');

ws.onopen = () => {
  console.log('Подключено к лидерборду');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'leaderboard_update') {
    const leaderboard = message.data;
    // Обновляем UI
    console.log('Обновление лидерборда:', leaderboard);
    // [
    //   { rank: 1, username: "...", total_points: 1300, ... },
    //   ...
    // ]
  }
};

ws.onclose = () => {
  console.log('Отключено от лидерборда');
  // Можно реализовать авто-переподключение
};`

  const consumerCode = `# api/consumers.py
from channels.generic.websocket import AsyncWebSocketConsumer
from channels.db import database_sync_to_async

class LeaderboardConsumer(AsyncWebSocketConsumer):
    async def connect(self):
        self.group_name = 'leaderboard'
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()
        # Отправляем текущий лидерборд
        data = await self.get_leaderboard()
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'data': data
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )

    async def leaderboard_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'data': event['data']
        }))`

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-2">⚡ WebSocket — Реалтайм лидерборд</h2>
        <p className="text-gray-300">
          Обновления лидерборда отправляются в реальном времени через Django Channels.
          При каждом успешном решении задача отправляется событие всем подключённым клиентам.
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">📡 Подключение</h3>
        <div className="bg-gray-800 rounded-lg p-3 font-mono text-sm text-green-400">
          ws://localhost:8000/ws/leaderboard/
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">📨 Формат сообщения</h3>
        <CodeBlock 
          code={`{
  "type": "leaderboard_update",
  "data": [
    {
      "rank": 1,
      "username": "Алексей Смирнов",
      "total_points": 1300,
      "solved_tasks": 8,
      "avg_time": 0.45,
      "avatar": "АС"
    }
  ]
}`}
          id="ws-message"
          copyCode={copyCode}
          copiedCode={copiedCode}
          language="json"
        />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">💻 Клиент (JavaScript)</h3>
        <CodeBlock code={clientCode} id="ws-client" copyCode={copyCode} copiedCode={copiedCode} language="javascript" />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">🐍 Сервер (Consumer)</h3>
        <CodeBlock code={consumerCode} id="ws-consumer" copyCode={copyCode} copiedCode={copiedCode} language="python" />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">⚙️ Когда отправляются обновления</h3>
        <ul className="space-y-2 text-sm text-gray-300">
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            При подключении нового клиента (текущий лидерборд)
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            После успешной проверки решения (submit)
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Периодически каждые 5 секунд для синхронизации
          </li>
        </ul>
      </div>
    </div>
  )
}

export default App
