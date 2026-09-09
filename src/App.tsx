import { useState } from 'react'

type Tab = 'compliance' | 'endpoints' | 'models' | 'setup' | 'websocket'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('compliance')
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'compliance', label: 'Соответствие', icon: '✅' },
    { id: 'endpoints', label: 'API Endpoints', icon: '🔌' },
    { id: 'models', label: 'Модели', icon: '🗄' },
    { id: 'setup', label: 'Запуск', icon: '🚀' },
    { id: 'websocket', label: 'WebSocket', icon: '⚡' },
  ]

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center font-bold text-lg">
              ⚔️
            </div>
            <div>
              <h1 className="text-xl font-bold">SQL Battle Backend</h1>
              <p className="text-xs text-gray-400">Django 4.2 • DRF • Совместим с фронтендом</p>
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

        <main>
          {activeTab === 'compliance' && <ComplianceTab />}
          {activeTab === 'endpoints' && <EndpointsTab copyCode={copyCode} copiedCode={copiedCode} />}
          {activeTab === 'models' && <ModelsTab />}
          {activeTab === 'setup' && <SetupTab copyCode={copyCode} copiedCode={copiedCode} />}
          {activeTab === 'websocket' && <WebSocketTab copyCode={copyCode} copiedCode={copiedCode} />}
        </main>
      </div>

      <footer className="border-t border-gray-800 mt-16 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>SQL Battle Backend • Django REST Framework • cdek_digital</p>
        </div>
      </footer>
    </div>
  )
}

function CodeBlock({ code, id, copyCode, copiedCode, language = 'bash' }: { 
  code: string; id: string; copyCode: (code: string, id: string) => void;
  copiedCode: string | null; language?: string;
}) {
  return (
    <div className="relative group">
      <div className="absolute top-2 right-2 flex items-center gap-2">
        <span className="text-xs text-gray-500">{language}</span>
        <button
          onClick={() => copyCode(code, id)}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition-colors opacity-0 group-hover:opacity-100"
        >
          {copiedCode === id ? '✓' : 'Copy'}
        </button>
      </div>
      <pre className="bg-gray-900 border border-gray-800 rounded-lg p-4 overflow-x-auto text-sm">
        <code className="text-gray-300">{code}</code>
      </pre>
    </div>
  )
}

function ComplianceTab() {
  const checks = [
    {
      category: '🔐 Аутентификация',
      items: [
        { name: 'POST /api/auth/register → { token, user }', ok: true, note: 'Фронтенд ожидает token (не access/refresh)' },
        { name: 'POST /api/auth/login → { token, user }', ok: true, note: 'Возвращаем один токен + данные пользователя' },
        { name: 'Authorization: Bearer <token>', ok: true, note: 'JWT через simplejwt, формат совместим' },
        { name: 'User: { id, username, email, rating, totalPoints, role }', ok: true, note: 'camelCase для totalPoints' },
      ]
    },
    {
      category: '👤 Профиль',
      items: [
        { name: 'GET /api/profile → { totalPoints, solvedTasks, rank }', ok: true, note: 'Все поля camelCase' },
        { name: 'solvedTasks — массив id решённых задач', ok: true, note: 'Из Submission где is_correct=True' },
        { name: 'rank — позиция в рейтинге', ok: true, note: 'Считается по total_points' },
      ]
    },
    {
      category: '🎮 Задачи',
      items: [
        { name: 'GET /api/tasks → [{ id, title, difficulty, points, status }]', ok: true, note: 'status: "solved" | "unsolved"' },
        { name: 'GET /api/tasks/{id} → { expectedResult }', ok: true, note: 'camelCase для expectedResult' },
        { name: 'POST /api/tasks/{id}/execute → { status, data, execution_time }', ok: true, note: 'SQLite sandbox, SELECT only' },
        { name: 'POST /api/tasks/{id}/submit → { is_correct, points_earned, new_total_points, expected_result }', ok: true, note: 'Сравнение результатов, не текста' },
      ]
    },
    {
      category: '🏆 Лидерборд',
      items: [
        { name: 'GET /api/leaderboard → [{ rank, username, totalPoints, solvedTasks, avgTime, avatar }]', ok: true, note: 'Все camelCase' },
        { name: 'WebSocket /ws/leaderboard → { type: "leaderboard_update", data: [...] }', ok: true, note: 'Обновление после submit' },
      ]
    },
    {
      category: '👥 Админка',
      items: [
        { name: 'GET /api/admin/users → [{ assignedTaskId }]', ok: true, note: 'camelCase assignedTaskId' },
        { name: 'POST /api/admin/users/{id}/assign → { taskId }', ok: true, note: 'Принимает camelCase taskId' },
        { name: 'POST /api/admin/users/{id}/clear', ok: true, note: 'Снимает назначение' },
        { name: 'GET /api/user/assigned-task → { id, title, difficulty, points }', ok: true, note: 'Для лобби' },
        { name: 'GET /api/admin/tasks → [{ expectedResult }]', ok: true, note: 'Полные данные задач' },
        { name: 'POST /api/admin/tasks → { expectedResult }', ok: true, note: 'Создание задачи' },
        { name: 'GET /api/admin/settings → { battle_start, round_duration_minutes }', ok: true, note: 'Настройки баттла' },
        { name: 'PUT /api/admin/settings', ok: true, note: 'Обновление настроек' },
      ]
    },
    {
      category: '🛡️ Безопасность',
      items: [
        { name: 'SQL Sandbox — только SELECT', ok: true, note: 'Запрет INSERT/UPDATE/DELETE/DROP/ALTER/CREATE' },
        { name: 'SQLite временная БД', ok: true, note: 'Каждый запрос в изолированной БД' },
        { name: 'Таймаут 3 секунды', ok: true, note: 'PRAGMA busy_timeout = 3000' },
        { name: 'Лимит 1000 строк', ok: true, note: 'fetchmany(1000)' },
      ]
    },
  ]

  const totalItems = checks.reduce((acc, cat) => acc + cat.items.length, 0)
  const okItems = checks.reduce((acc, cat) => acc + cat.items.filter(i => i.ok).length, 0)

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-2">✅ Полное соответствие фронтенду</h2>
        <p className="text-gray-300 mb-4">
          Бэкенд полностью совместим с API-контрактом из README и реальным кодом <code className="text-green-400">lib/api.ts</code> фронтенда.
          Все форматы camelCase, все эндпоинты реализованы.
        </p>
        <div className="flex items-center gap-4">
          <div className="bg-green-900/30 border border-green-800 rounded-lg px-4 py-2">
            <span className="text-green-400 font-bold text-lg">{okItems}/{totalItems}</span>
            <span className="text-gray-400 text-sm ml-2">совпадений</span>
          </div>
          <div className="bg-gray-800 rounded-lg px-4 py-2">
            <span className="text-gray-300 text-sm">Base URL: </span>
            <code className="text-green-400">http://localhost:8000/api</code>
          </div>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">📋 Сравнение с README фронтенда</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-800">
                <th className="px-3 py-2">Параметр</th>
                <th className="px-3 py-2">README фронтенда</th>
                <th className="px-3 py-2">Реальный код (lib/api.ts)</th>
                <th className="px-3 py-2">Бэкенд</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">JWT формат</td>
                <td className="px-3 py-2"><code className="text-blue-400">{'{ token, user }'}</code></td>
                <td className="px-3 py-2 text-gray-400">setToken(token) — один токен</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ {`{ token, user }`}</span></td>
              </tr>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">User формат</td>
                <td className="px-3 py-2"><code className="text-blue-400">total_points</code></td>
                <td className="px-3 py-2 text-gray-400">totalPoints (camelCase)</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ totalPoints</span></td>
              </tr>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">Task detail</td>
                <td className="px-3 py-2"><code className="text-blue-400">expected_result</code></td>
                <td className="px-3 py-2 text-gray-400">expectedResult (camelCase)</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ expectedResult</span></td>
              </tr>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">Assign body</td>
                <td className="px-3 py-2"><code className="text-blue-400">{'{ task_id }'}</code></td>
                <td className="px-3 py-2 text-gray-400">{'{ taskId }'} (camelCase)</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ taskId</span></td>
              </tr>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">Admin users</td>
                <td className="px-3 py-2"><code className="text-blue-400">assigned_task_id</code></td>
                <td className="px-3 py-2 text-gray-400">assignedTaskId (camelCase)</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ assignedTaskId</span></td>
              </tr>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">Settings</td>
                <td className="px-3 py-2 text-gray-500">не описан</td>
                <td className="px-3 py-2 text-gray-400">GET/PUT /admin/settings</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ реализован</span></td>
              </tr>
              <tr className="border-b border-gray-800/50">
                <td className="px-3 py-2 text-gray-300">Leaderboard</td>
                <td className="px-3 py-2"><code className="text-blue-400">total_points</code></td>
                <td className="px-3 py-2 text-gray-400">totalPoints (camelCase)</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ totalPoints</span></td>
              </tr>
              <tr>
                <td className="px-3 py-2 text-gray-300">WebSocket URL</td>
                <td className="px-3 py-2"><code className="text-blue-400">ws://...:8000/ws/leaderboard</code></td>
                <td className="px-3 py-2 text-gray-400">.replace('/api', '/ws') + '/leaderboard'</td>
                <td className="px-3 py-2"><span className="text-green-400">✓ /ws/leaderboard/</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {checks.map((category) => (
        <div key={category.category} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-800/30">
            <h3 className="font-semibold text-lg">{category.category}</h3>
          </div>
          <div className="divide-y divide-gray-800/50">
            {category.items.map((item, idx) => (
              <div key={idx} className="flex items-center gap-3 px-4 py-3 hover:bg-gray-800/30">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                  item.ok ? 'bg-green-900/50 text-green-400 border border-green-800' : 'bg-red-900/50 text-red-400 border border-red-800'
                }`}>
                  {item.ok ? '✓' : '✗'}
                </span>
                <div className="flex-1 min-w-0">
                  <code className="text-sm text-gray-200 font-mono">{item.name}</code>
                  <p className="text-xs text-gray-500 mt-0.5">{item.note}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function EndpointsTab({ copyCode, copiedCode }: { copyCode: (code: string, id: string) => void; copiedCode: string | null }) {
  const endpoints = [
    {
      section: '🔐 Аутентификация',
      items: [
        { method: 'POST', path: '/api/auth/register', desc: 'Регистрация', auth: false,
          body: '{"username": "ivan.petrov", "email": "ivan@cdek.digital", "password": "secure_password"}',
          response: '{"token": "eyJhbGci...", "user": {"id": 1, "username": "ivan.petrov", "email": "ivan@cdek.digital", "rating": 0, "totalPoints": 0, "role": "participant"}}' },
        { method: 'POST', path: '/api/auth/login', desc: 'Вход', auth: false,
          body: '{"username": "ivan.petrov", "password": "secure_password"}',
          response: '{"token": "eyJhbGci...", "user": {"id": 1, "username": "ivan.petrov", "totalPoints": 450, "role": "participant"}}' },
      ]
    },
    {
      section: '👤 Профиль',
      items: [
        { method: 'GET', path: '/api/profile', desc: 'Данные пользователя', auth: true,
          response: '{"id": 1, "username": "ivan.petrov", "email": "ivan@cdek.digital", "rating": 1250, "totalPoints": 450, "rank": 3, "solvedTasks": [1, 2, 5], "role": "participant"}' },
      ]
    },
    {
      section: '🎮 Задачи',
      items: [
        { method: 'GET', path: '/api/tasks', desc: 'Список задач', auth: true,
          response: '[{"id": 1, "title": "Найди активных хакеров", "difficulty": "easy", "points": 100, "status": "unsolved"}]' },
        { method: 'GET', path: '/api/tasks/{id}', desc: 'Детали задачи', auth: true,
          response: '{"id": 3, "title": "Анализ заказов", "description": "...", "difficulty": "hard", "points": 500, "schema": "CREATE TABLE...", "tables": [...], "expectedResult": [...]}' },
        { method: 'POST', path: '/api/tasks/{id}/execute', desc: 'Выполнить запрос (Run)', auth: true,
          body: '{"query": "SELECT name FROM users WHERE status = \'active\'"}',
          response: '{"status": "success", "data": [{"name": "Иван Петров"}], "execution_time": 0.045}' },
        { method: 'POST', path: '/api/tasks/{id}/submit', desc: 'Отправить решение', auth: true,
          body: '{"query": "SELECT city, COUNT(*) FROM users GROUP BY city"}',
          response: '{"is_correct": true, "points_earned": 100, "new_total_points": 550, "expected_result": [...]}' },
      ]
    },
    {
      section: '🏆 Лидерборд',
      items: [
        { method: 'GET', path: '/api/leaderboard', desc: 'Топ участников', auth: false,
          response: '[{"rank": 1, "username": "Алексей Смирнов", "totalPoints": 1250, "solvedTasks": 8, "avgTime": 0.45, "avatar": "АС"}]' },
      ]
    },
    {
      section: '👥 Админка',
      items: [
        { method: 'GET', path: '/api/admin/users', desc: 'Все пользователи', auth: true, admin: true,
          response: '[{"id": 1, "username": "ivan.petrov", "email": "ivan@cdek.digital", "rating": 1250, "totalPoints": 450, "assignedTaskId": 3}]' },
        { method: 'POST', path: '/api/admin/users/{id}/assign', desc: 'Назначить задачу', auth: true, admin: true,
          body: '{"taskId": 3}',
          response: '{"success": true, "message": "Задача назначена"}' },
        { method: 'POST', path: '/api/admin/users/{id}/clear', desc: 'Снять назначение', auth: true, admin: true,
          response: '{"success": true, "message": "Назначение снято"}' },
        { method: 'GET', path: '/api/user/assigned-task', desc: 'Назначенная задача', auth: true,
          response: '{"id": 3, "title": "Анализ заказов", "difficulty": "hard", "points": 500}' },
        { method: 'GET', path: '/api/admin/tasks', desc: 'Все задачи (админ)', auth: true, admin: true,
          response: '[{"id": 1, "title": "...", "expectedResult": [...]}]' },
        { method: 'POST', path: '/api/admin/tasks', desc: 'Создать задачу', auth: true, admin: true,
          body: '{"title": "...", "description": "...", "difficulty": "medium", "points": 250, "schema": "...", "tables": [...], "expectedResult": [...]}',
          response: '{"id": 10, "title": "Новая задача", "success": true}' },
        { method: 'GET', path: '/api/admin/settings', desc: 'Настройки', auth: true, admin: true,
          response: '{"battle_start": "2026-09-15T10:00:00Z", "round_duration_minutes": 120}' },
        { method: 'PUT', path: '/api/admin/settings', desc: 'Обновить настройки', auth: true, admin: true,
          body: '{"battle_start": "2026-09-15T10:00:00Z", "round_duration_minutes": 90}' },
      ]
    },
  ]

  return (
    <div className="space-y-8">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-sm text-gray-400">
          <span className="text-yellow-400 font-mono">Base URL:</span>{' '}
          <code className="text-green-400">http://localhost:8000/api</code>
          {' • '}
          <span className="text-yellow-400 font-mono">Auth:</span>{' '}
          <code className="text-green-400">Authorization: Bearer {'<token>'}</code>
          {' • '}
          <span className="text-yellow-400">Все ответы camelCase</span>
        </p>
      </div>

      {endpoints.map((section) => (
        <div key={section.section} className="space-y-3">
          <h3 className="text-lg font-semibold">{section.section}</h3>
          <div className="space-y-2">
            {section.items.map((ep, idx) => (
              <EndpointCard key={idx} endpoint={ep} copyCode={copyCode} copiedCode={copiedCode} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function EndpointCard({ endpoint, copyCode, copiedCode }: { 
  endpoint: any; copyCode: (code: string, id: string) => void; copiedCode: string | null;
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
          AUTH_USER_MODEL = 'api.User'. Совпадают со схемой из README фронтенда.
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
      code: `# Кастомная команда
python manage.py create_admin --username admin --password admin123`
    },
    {
      title: '7. Запуск сервера',
      code: `# Разработка
python manage.py runserver 0.0.0.0:8000

# Продакшен
gunicorn sql_battle.wsgi:application --bind 0.0.0.0:8000`
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
        <h3 className="font-semibold mb-3">🐳 Docker (опционально)</h3>
        <CodeBlock 
          code={`# Запуск с PostgreSQL
docker-compose up -d

# Или только бэкенд с SQLite
docker build -t sql-battle-backend .
docker run -p 8000:8000 sql-battle-backend`}
          id="docker-run"
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
            <li>• <code className="text-green-400">POST /api/auth/login</code> — вход</li>
            <li>• <code className="text-green-400">GET /api/leaderboard</code> — лидерборд</li>
            <li>• <code className="text-green-400">GET /api/tasks</code> — список задач (с токеном)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function WebSocketTab({ copyCode, copiedCode }: { copyCode: (code: string, id: string) => void; copiedCode: string | null }) {
  const clientCode = `// Фронтенд подключается так (из lib/api.ts):
const wsUrl = API_BASE_URL.replace('http://', 'ws://').replace('/api', '/ws');
const ws = new WebSocket(\`\${wsUrl}/leaderboard\`);
// Результат: ws://localhost:8000/ws/leaderboard

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "leaderboard_update") {
    onUpdate(data.data);
    // data.data = [
    //   { rank: 1, username: "...", totalPoints: 1300, solvedTasks: 8, avgTime: 0.45, avatar: "АС" }
    // ]
  }
};`

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-2">⚡ WebSocket — Реалтайм лидерборд</h2>
        <p className="text-gray-300">
          Обновления лидерборда через Django Channels. Совместимо с <code className="text-green-400">connectLeaderboardWebSocket()</code> из фронтенда.
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">📡 URL подключения</h3>
        <div className="bg-gray-800 rounded-lg p-3 font-mono text-sm text-green-400">
          ws://localhost:8000/ws/leaderboard/
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Фронтенд формирует URL: <code>API_BASE_URL.replace('http://', 'ws://').replace('/api', '/ws')</code> + <code>/leaderboard</code>
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">📨 Формат сообщения (camelCase)</h3>
        <CodeBlock 
          code={`{
  "type": "leaderboard_update",
  "data": [
    {
      "rank": 1,
      "username": "Алексей Смирнов",
      "totalPoints": 1250,
      "solvedTasks": 8,
      "avgTime": 0.45,
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
        <h3 className="font-semibold mb-3">💻 Клиент (из lib/api.ts)</h3>
        <CodeBlock code={clientCode} id="ws-client" copyCode={copyCode} copiedCode={copiedCode} language="javascript" />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">⚙️ Когда отправляются обновления</h3>
        <ul className="space-y-2 text-sm text-gray-300">
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            При подключении нового клиента
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            После успешной проверки решения (submit)
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Каждые 5 секунд для синхронизации
          </li>
        </ul>
      </div>
    </div>
  )
}

export default App
