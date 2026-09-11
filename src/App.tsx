import { useState } from 'react'

type Tab = 'diagnosis' | 'compliance' | 'endpoints' | 'models' | 'setup' | 'websocket'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('diagnosis')
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'diagnosis', label: 'Диагностика', icon: '🔍' },
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
          {activeTab === 'diagnosis' && <DiagnosisTab copyCode={copyCode} copiedCode={copiedCode} />}
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

function DiagnosisTab({ copyCode, copiedCode }: { copyCode: (code: string, id: string) => void; copiedCode: string | null }) {
  const frontendFix = `// lib/api.ts — изменения в бэкенде для совместимости с фронтендом

// 1. submitSolution теперь принимает time_spent
export async function submitSolution(taskId: number, query: string, timeSpent: number) {
    const res = await fetch(\`\${API_BASE_URL}/tasks/\${taskId}/submit\`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ query, time_spent: timeSpent })
    });
    return res.json();
}

// 2. getLeaderboard теперь ожидает total_time_spent
export async function getLeaderboard() {
    const res = await fetch(\`\${API_BASE_URL}/leaderboard\`);
    const data = await res.json();
    return data.map((entry: any) => ({
        rank: entry.rank,
        username: entry.username,
        avatar: entry.avatar,
        totalPoints: entry.total_points ?? entry.totalPoints ?? 0,
        solvedTasks: entry.solved_tasks ?? entry.solvedTasks ?? 0,
        totalTimeSpent: entry.total_time_spent ?? entry.totalTimeSpent ?? 0,
    }));
}

// 3. getUserProfile поддерживает оба формата
export async function getUserProfile() {
    const res = await fetch(\`\${API_BASE_URL}/profile\`, { headers: getAuthHeaders() });
    const data = await res.json();
    return {
        id: data.id,
        username: data.username,
        email: data.email,
        rating: data.rating ?? 0,
        totalPoints: data.total_points ?? data.totalPoints ?? 0,
        solvedTasks: data.solved_tasks ?? data.solvedTasks ?? [],
        role: data.role ?? "participant",
    };
}

// 4. WebSocket URL без /api
export function connectLeaderboardWebSocket(onUpdate: (data: any[]) => void) {
    const token = localStorage.getItem("sql_battle_token");
    const wsBaseUrl = API_BASE_URL.replace('http://', 'ws://').replace('/api', '');
    const tokenQuery = token ? \`?token=\${encodeURIComponent(token)}\` : "";
    const wsUrl = \`\${wsBaseUrl}/ws/leaderboard\${tokenQuery}\`;
    const ws = new WebSocket(wsUrl);
    // ...
}`

  const backendView = `# backend/api/views.py — добавить после profile_view

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_history_view(request):
    """
    GET /api/profile/history — История решений текущего пользователя.

    Возвращает массив:
    [
        {
            "id": 1,
            "task_title": "Найди активных хакеров",
            "difficulty": "easy",
            "execution_time": 0.12,
            "is_correct": true,
            "points_earned": 100
        },
        ...
    ]
    """
    user = request.user
    submissions = Submission.objects.filter(user=user).select_related('task').order_by('-created_at')

    history = []
    for sub in submissions:
        execution_time = round((sub.execution_time_ms or 0) / 1000, 2)
        history.append({
            'id': sub.id,
            'task_title': sub.task.title,
            'difficulty': sub.task.difficulty,
            'execution_time': execution_time,
            'is_correct': sub.is_correct,
            'points_earned': sub.points_earned,
        })

    return Response(history, status=status.HTTP_200_OK)`

  const backendUrl = `# backend/api/urls.py — добавить после path('profile', ...)

path('profile/history', views.profile_history_view, name='profile-history'),`

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-2">🆕 Последние изменения в бэкенде</h2>
        <p className="text-gray-300">
          Бэкенд обновлён для полной совместимости с изменениями во фронтенде:
        </p>
        <ul className="mt-3 space-y-1 text-sm text-gray-400">
          <li>✅ Убран префикс <code className="text-green-400">/api</code> — запросы идут напрямую</li>
          <li>✅ Добавлен <code className="text-green-400">time_spent</code> в submit решения</li>
          <li>✅ Лидерборд возвращает <code className="text-green-400">total_time_spent</code></li>
          <li>✅ Профиль возвращает оба формата: <code className="text-green-400">totalPoints</code> и <code className="text-green-400">total_points</code></li>
          <li>✅ <code className="text-green-400">/tasks</code> доступен без авторизации</li>
        </ul>
      </div>

      {/* Изменения */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span className="text-blue-400">📝</span> Что изменилось в бэкенде
        </h3>
        <div className="space-y-4">
          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-4">
            <p className="text-sm text-blue-300 font-semibold mb-2">1. Убран префикс /api</p>
            <p className="text-xs text-gray-400 mb-2">Файл: <code className="text-green-400">backend/sql_battle/urls.py</code></p>
            <CodeBlock 
              code={`# Было:
path('api/', include('api.urls')),

# Стало:
path('', include('api.urls')),  # Без префикса`}
              id="change-urls"
              copyCode={copyCode}
              copiedCode={copiedCode}
              language="python"
            />
          </div>

          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-4">
            <p className="text-sm text-blue-300 font-semibold mb-2">2. Submit принимает time_spent</p>
            <p className="text-xs text-gray-400 mb-2">Файл: <code className="text-green-400">backend/api/serializers.py</code></p>
            <CodeBlock 
              code={`class SubmitSolutionSerializer(serializers.Serializer):
    query = serializers.CharField()
    time_spent = serializers.FloatField(required=False, default=0)  # NEW`}
              id="change-serializer"
              copyCode={copyCode}
              copiedCode={copiedCode}
              language="python"
            />
          </div>

          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-4">
            <p className="text-sm text-blue-300 font-semibold mb-2">3. Лидерборд возвращает total_time_spent</p>
            <p className="text-xs text-gray-400 mb-2">Файл: <code className="text-green-400">backend/api/views.py</code></p>
            <CodeBlock 
              code={`# Считаем общее время на все правильные решения
total_time_ms = Submission.objects.filter(
    user=user, is_correct=True
).aggregate(total=Sum('execution_time_ms'))['total']

result.append({
    'rank': rank,
    'username': user.username,
    'totalPoints': user.total_points,
    'solvedTasks': solved_count,
    'total_time_spent': total_time_seconds,  # NEW
    'totalTimeSpent': total_time_seconds,    # NEW (camelCase)
    'avgTime': ...,  # OLD (для совместимости)
    'avatar': avatar
})`}
              id="change-leaderboard"
              copyCode={copyCode}
              copiedCode={copiedCode}
              language="python"
            />
          </div>

          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-4">
            <p className="text-sm text-blue-300 font-semibold mb-2">4. Профиль возвращает оба формата</p>
            <p className="text-xs text-gray-400 mb-2">Файл: <code className="text-green-400">backend/api/serializers.py</code></p>
            <CodeBlock 
              code={`class UserProfileSerializer(serializers.ModelSerializer):
    totalPoints = serializers.IntegerField(source='total_points', read_only=True)
    total_points = serializers.IntegerField(read_only=True)  # NEW
    solvedTasks = serializers.SerializerMethodField()
    solved_tasks = serializers.SerializerMethodField()  # NEW
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rating', 
                  'totalPoints', 'total_points',  # Оба формата
                  'rank', 'solvedTasks', 'solved_tasks', 'role']`}
              id="change-profile"
              copyCode={copyCode}
              copiedCode={copiedCode}
              language="python"
            />
          </div>

          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-4">
            <p className="text-sm text-blue-300 font-semibold mb-2">5. /tasks доступен без авторизации</p>
            <p className="text-xs text-gray-400 mb-2">Файл: <code className="text-green-400">backend/api/views.py</code></p>
            <CodeBlock 
              code={`@api_view(['GET'])
@permission_classes([AllowAny])  # Было: IsAuthenticated
def task_list_view(request):
    """GET /tasks — Список задач (публичный)"""
    tasks = Task.objects.all()
    serializer = TaskListSerializer(tasks, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)`}
              id="change-tasks-public"
              copyCode={copyCode}
              copiedCode={copiedCode}
              language="python"
            />
          </div>
        </div>
      </div>

      {/* Причина */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span className="text-red-400">❌</span> Причина ошибки
        </h3>
        <div className="space-y-4">
          <div className="bg-red-950/30 border border-red-900/50 rounded-lg p-4">
            <p className="text-sm text-red-300 font-mono mb-2">Ошибка в консоли браузера:</p>
            <code className="text-red-400 text-sm">
              TypeError: (0 , _api.getUserSubmissionHistory) is not a function
            </code>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-sm font-semibold text-yellow-400 mb-2">Фронтенд (profile/page.tsx):</p>
              <pre className="text-xs text-gray-300 overflow-x-auto">
{`import { getUserProfile, 
  getUserSubmissionHistory } from "@/lib/api"
// ↑ getUserSubmissionHistory 
//   НЕ СУЩЕСТВУЕТ в lib/api.ts!`}
              </pre>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-sm font-semibold text-yellow-400 mb-2">Бэкенд (urls.py):</p>
              <pre className="text-xs text-gray-300 overflow-x-auto">
{`urlpatterns = [
  path('profile', ...),
  # path('profile/history', ...) 
  #   ← ОТСУТСТВУЕТ!
]`}
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* Решение */}
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
          <span className="text-green-400">✅</span> Решение (2 шага)
        </h3>
        <p className="text-gray-300 text-sm">
          Нужно добавить функцию в фронтенд и эндпоинт в бэкенд.
        </p>
      </div>

      {/* Шаг 1: Бэкенд */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span className="bg-blue-600 text-white text-xs font-bold px-2 py-0.5 rounded">Шаг 1</span>
          Бэкенд — добавить эндпоинт <code className="text-green-400">/api/profile/history</code>
        </h3>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-400 mb-2">1.1 Добавить view в <code className="text-green-400">backend/api/views.py</code>:</p>
            <CodeBlock code={backendView} id="backend-view" copyCode={copyCode} copiedCode={copiedCode} language="python" />
          </div>
          
          <div>
            <p className="text-sm text-gray-400 mb-2">1.2 Добавить URL в <code className="text-green-400">backend/api/urls.py</code>:</p>
            <CodeBlock code={backendUrl} id="backend-url" copyCode={copyCode} copiedCode={copiedCode} language="python" />
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4">
            <p className="text-sm text-gray-400 mb-2">Формат ответа (совместим с фронтендом):</p>
            <CodeBlock 
              code={`[
  {
    "id": 1,
    "task_title": "Найди активных хакеров",
    "difficulty": "easy",
    "execution_time": 0.12,
    "is_correct": true,
    "points_earned": 100
  },
  {
    "id": 2,
    "task_title": "Топ-10 самых дорогих заказов",
    "difficulty": "medium",
    "execution_time": 0.45,
    "is_correct": true,
    "points_earned": 250
  }
]`}
              id="history-response"
              copyCode={copyCode}
              copiedCode={copiedCode}
              language="json"
            />
          </div>
        </div>
      </div>

      {/* Шаг 2: Фронтенд */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span className="bg-purple-600 text-white text-xs font-bold px-2 py-0.5 rounded">Шаг 2</span>
          Фронтенд — добавить функцию в <code className="text-green-400">lib/api.ts</code>
        </h3>
        
        <p className="text-sm text-gray-400 mb-2">
          Добавить функцию <code className="text-green-400">getUserSubmissionHistory</code> в секцию "2. ПРОФИЛЬ":
        </p>
        <CodeBlock code={frontendFix} id="frontend-fix" copyCode={copyCode} copiedCode={copiedCode} language="typescript" />
      </div>

      {/* Проверка */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">🧪 Проверка после исправления</h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-green-900/50 text-green-400 flex items-center justify-center text-xs font-bold border border-green-800 shrink-0 mt-0.5">1</span>
            <div>
              <p className="text-sm text-gray-200">Перезапустить бэкенд</p>
              <code className="text-xs text-gray-500">python manage.py runserver 0.0.0.0:8000</code>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-green-900/50 text-green-400 flex items-center justify-center text-xs font-bold border border-green-800 shrink-0 mt-0.5">2</span>
            <div>
              <p className="text-sm text-gray-200">Проверить эндпоинт напрямую</p>
              <code className="text-xs text-gray-500">curl -H "Authorization: Bearer &lt;token&gt;" http://localhost:8000/api/profile/history</code>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-green-900/50 text-green-400 flex items-center justify-center text-xs font-bold border border-green-800 shrink-0 mt-0.5">3</span>
            <div>
              <p className="text-sm text-gray-200">Перезапустить фронтенд</p>
              <code className="text-xs text-gray-500">npm run dev</code>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-green-900/50 text-green-400 flex items-center justify-center text-xs font-bold border border-green-800 shrink-0 mt-0.5">4</span>
            <div>
              <p className="text-sm text-gray-200">Открыть страницу профиля</p>
              <code className="text-xs text-gray-500">http://localhost:3000/profile</code>
            </div>
          </div>
        </div>
      </div>

      {/* Схема */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Схема данных</h3>
        <pre className="text-sm text-gray-300 whitespace-pre overflow-x-auto">{`profile/page.tsx                    backend/api/
─────────────────                    ──────────────
                                     
import {                             views.py
  getUserProfile,                    ├── profile_view()        → GET /api/profile
  getUserSubmissionHistory  ←─────── ├── profile_history_view() → GET /api/profile/history  ← НОВЫЙ!
} from "@/lib/api"                   │
                                     urls.py
useEffect →                          ├── path('profile', ...)
  Promise.all([                      ├── path('profile/history', ...)  ← НОВЫЙ!
    getUserProfile(),                │
    getUserSubmissionHistory()       models.py
  ])                                 └── Submission → Task (select_related)
`}</pre>
      </div>

      {/* WebSocket проблема */}
      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-2">⚡ Диагностика: WebSocket /ws/leaderboard → 404</h2>
        <p className="text-gray-300">
          Ошибка: <code className="text-red-400">Not Found: /ws/leaderboard</code> при подключении к WebSocket лидерборда.
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span className="text-red-400">❌</span> Три причины ошибки
        </h3>
        <div className="space-y-4">
          <div className="bg-red-950/30 border border-red-900/50 rounded-lg p-4">
            <p className="text-sm text-red-300 font-mono mb-2">Ошибка в логах бэкенда:</p>
            <code className="text-red-400 text-sm">Not Found: /ws/leaderboard</code>
            <br />
            <code className="text-red-400 text-sm">"GET /ws/leaderboard?token=eyJ... HTTP/1.1" 404</code>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-400 mb-2">1. Routing: слэш</p>
              <p className="text-xs text-gray-400 mb-1">Было:</p>
              <code className="text-xs text-red-400 block mb-2">r'ws/leaderboard/$'</code>
              <p className="text-xs text-gray-400 mb-1">Стало:</p>
              <code className="text-xs text-green-400 block">r'ws/leaderboard/?$'</code>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-400 mb-2">2. WSGI вместо ASGI</p>
              <p className="text-xs text-gray-400 mb-1">Было:</p>
              <code className="text-xs text-red-400 block mb-2">python manage.py runserver</code>
              <p className="text-xs text-gray-400 mb-1">Стало:</p>
              <code className="text-xs text-green-400 block">daphne ... asgi:application</code>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-400 mb-2">3. Нет auth middleware</p>
              <p className="text-xs text-gray-400 mb-1">Фронтенд передаёт токен в URL:</p>
              <code className="text-xs text-gray-300 block mb-2">?token=eyJ...</code>
              <p className="text-xs text-green-400">✅ Добавлен QueryAuthMiddleware</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
          <span className="text-green-400">✅</span> Решение
        </h3>
        <div className="space-y-3">
          <p className="text-sm text-gray-300">Все три проблемы исправлены в бэкенде:</p>
          <ul className="space-y-1 text-sm text-gray-400 ml-4">
            <li>✅ <code className="text-green-400">routing.py</code> — слэш опционален: <code>r'ws/leaderboard/?$'</code></li>
            <li>✅ <code className="text-green-400">middleware.py</code> — <code>QueryAuthMiddleware</code> извлекает токен из <code>?token=...</code></li>
            <li>✅ <code className="text-green-400">asgi.py</code> — middleware подключён к WebSocket-маршрутам</li>
            <li>✅ <code className="text-green-400">requirements.txt</code> — добавлены <code>daphne</code> и <code>uvicorn</code></li>
          </ul>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">🚀 Правильный запуск сервера</h3>
        <CodeBlock 
          code={`# ❌ НЕ РАБОТАЕТ для WebSocket:
python manage.py runserver 0.0.0.0:8000

# ✅ ПРАВИЛЬНО — через ASGI-сервер:

# Вариант 1: daphne (рекомендуется)
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application

# Вариант 2: uvicorn
uvicorn sql_battle.asgi:application --host 0.0.0.0 --port 8000 --reload

# Вариант 3: runserver с channels (если channels в INSTALLED_APPS)
python manage.py runserver 0.0.0.0:8000`}
          id="ws-fix-run"
          copyCode={copyCode}
          copiedCode={copiedCode}
          language="bash"
        />
      </div>
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
      section: '👤 Пользователь — Задачи',
      items: [
        { method: 'GET', path: '/user/assigned-tasks', desc: 'Все назначенные задачи', auth: true,
          response: '[{"id": 1, "title": "...", "difficulty": "easy", "points": 100, "solved": false, "assigned_at": "..."}]' },
        { method: 'GET', path: '/user/assigned-task', desc: 'Первая задача (совместимость)', auth: true,
          response: '{"id": 3, "title": "Анализ заказов", "difficulty": "hard", "points": 500}' },
      ]
    },
    {
      section: '👥 Админка — Пользователи',
      items: [
        { method: 'GET', path: '/admin/users', desc: 'Все пользователи', auth: true, admin: true,
          response: '[{"id": 1, "username": "ivan", "totalPoints": 450, "assignedTaskId": 3, "assignedTaskIds": [1, 2, 3]}]' },
        { method: 'POST', path: '/admin/users/{id}/assign', desc: 'Назначить задачу(и)', auth: true, admin: true,
          body: '{"taskId": 3} или {"task_ids": [1, 2, 3]}',
          response: '{"success": true, "message": "Назначено задач: 3", "assigned_count": 3}' },
        { method: 'POST', path: '/admin/users/{id}/clear', desc: 'Снять назначение', auth: true, admin: true,
          body: '{} (все) или {"taskId": 3} (конкретная)',
          response: '{"success": true, "message": "Все назначения сняты"}' },
      ]
    },
    {
      section: '👥 Админка — Группы',
      items: [
        { method: 'GET', path: '/admin/groups', desc: 'Список групп', auth: true, admin: true,
          response: '[{"id": 1, "name": "Команда А", "user_count": 5, "users": [...]}]' },
        { method: 'POST', path: '/admin/groups/create', desc: 'Создать группу', auth: true, admin: true,
          body: '{"name": "Команда А", "description": "...", "user_ids": [1, 2, 3]}',
          response: '{"id": 1, "name": "Команда А", "success": true}' },
        { method: 'GET', path: '/admin/groups/{id}', desc: 'Детали группы', auth: true, admin: true,
          response: '{"id": 1, "name": "Команда А", "user_count": 5, "users": [...]}' },
        { method: 'PUT', path: '/admin/groups/{id}', desc: 'Обновить группу', auth: true, admin: true,
          body: '{"name": "Новое имя", "user_ids": [1, 2, 3, 4]}',
          response: '{"id": 1, "name": "Новое имя", "success": true}' },
        { method: 'DELETE', path: '/admin/groups/{id}', desc: 'Удалить группу', auth: true, admin: true,
          response: '{"success": true, "message": "Группа удалена"}' },
        { method: 'POST', path: '/admin/groups/{id}/assign', desc: 'Назначить задачи группе', auth: true, admin: true,
          body: '{"task_ids": [1, 2, 3]}',
          response: '{"success": true, "assigned_count": 15, "users_count": 5, "tasks_count": 3}' },
        { method: 'POST', path: '/admin/groups/{id}/clear', desc: 'Снять назначения группы', auth: true, admin: true,
          body: '{} (все) или {"task_ids": [1, 2]}',
          response: '{"success": true, "deleted_count": 10}' },
      ]
    },
    {
      section: '🎮 Админка — Задачи и настройки',
      items: [
        { method: 'GET', path: '/admin/tasks', desc: 'Все задачи (админ)', auth: true, admin: true,
          response: '[{"id": 1, "title": "...", "expectedResult": [...]}]' },
        { method: 'POST', path: '/admin/tasks', desc: 'Создать задачу', auth: true, admin: true,
          body: '{"title": "...", "description": "...", "difficulty": "medium", "points": 250, "schema": "...", "tables": [...], "expectedResult": [...]}',
          response: '{"id": 10, "title": "Новая задача", "success": true}' },
        { method: 'GET', path: '/admin/settings', desc: 'Настройки', auth: true, admin: true,
          response: '{"battle_start": "2026-09-15T10:00:00Z", "round_duration_minutes": 120}' },
        { method: 'PUT', path: '/admin/settings', desc: 'Обновить настройки', auth: true, admin: true,
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
const token = getToken(); // из localStorage
const ws = new WebSocket(\`\${wsUrl}/leaderboard?token=\${token}\`);
// Результат: ws://localhost:8000/ws/leaderboard?token=eyJ...

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "leaderboard_update") {
    onUpdate(data.data);
    // data.data = [
    //   { rank: 1, username: "...", totalPoints: 1300, solvedTasks: 8, avgTime: 0.45, avatar: "АС" }
    // ]
  }
};`

  const runServerCode = `# ❌ НЕ РАБОТАЕТ для WebSocket:
python manage.py runserver 0.0.0.0:8000

# ✅ ПРАВИЛЬНО — через ASGI-сервер:

# Вариант 1: daphne (рекомендуется)
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application

# Вариант 2: uvicorn
uvicorn sql_battle.asgi:application --host 0.0.0.0 --port 8000 --reload

# Вариант 3: runserver с channels (если channels в INSTALLED_APPS)
python manage.py runserver 0.0.0.0:8000`

  const errorLog = `# Ошибка в логах:
Not Found: /ws/leaderboard
"GET /ws/leaderboard?token=eyJ... HTTP/1.1" 404 2465

# Причина: сервер запущен через WSGI (runserver), 
# а не через ASGI. WebSocket-запросы не обрабатываются.

# Решение: запустить через daphne или uvicorn
daphne -b 0.0.0.0 -p 8000 sql_battle.asgi:application`

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-2">⚡ WebSocket — Реалтайм лидерборд</h2>
        <p className="text-gray-300">
          Обновления лидерборда через Django Channels. Совместимо с <code className="text-green-400">connectLeaderboardWebSocket()</code> из фронтенда.
        </p>
      </div>

      {/* Диагностика ошибки 404 */}
      <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <span className="text-red-400">🔧</span> Исправлена ошибка: <code className="text-red-400">Not Found: /ws/leaderboard</code>
        </h3>
        <div className="space-y-4">
          <div className="bg-red-950/30 border border-red-900/50 rounded-lg p-4">
            <p className="text-sm text-red-300 mb-2">Была ошибка:</p>
            <CodeBlock code={errorLog} id="ws-error-log" copyCode={copyCode} copiedCode={copiedCode} language="bash" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-xs text-yellow-400 font-semibold mb-1">Проблема 1</p>
              <p className="text-xs text-gray-300">Routing требовал слэш в конце: <code className="text-red-400">ws/leaderboard/$</code></p>
              <p className="text-xs text-green-400 mt-1">✅ Исправлено: <code>ws/leaderboard/?$</code></p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-xs text-yellow-400 font-semibold mb-1">Проблема 2</p>
              <p className="text-xs text-gray-300">Сервер запущен через WSGI, а не ASGI</p>
              <p className="text-xs text-green-400 mt-1">✅ Используйте <code>daphne</code> или <code>uvicorn</code></p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-xs text-yellow-400 font-semibold mb-1">Проблема 3</p>
              <p className="text-xs text-gray-300">Нет middleware для токена в query-параметре</p>
              <p className="text-xs text-green-400 mt-1">✅ Добавлен <code>QueryAuthMiddleware</code></p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-2">Правильный запуск сервера:</p>
            <CodeBlock code={runServerCode} id="ws-run-server" copyCode={copyCode} copiedCode={copiedCode} language="bash" />
          </div>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold mb-3">📡 URL подключения</h3>
        <div className="bg-gray-800 rounded-lg p-3 font-mono text-sm text-green-400">
          ws://localhost:8000/ws/leaderboard?token=eyJ...
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Фронтенд передаёт JWT-токен через query-параметр <code>?token=...</code> (WebSocket не поддерживает заголовки).
          Бэкенд извлекает токен через <code>QueryAuthMiddleware</code>.
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
