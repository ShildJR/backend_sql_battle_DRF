# 🚀 Инструкция по запуску после синхронизации

## ✅ Все изменения внесены

Бэкенд полностью синхронизирован с фронтендом согласно CHANGELOG.md.

---

## 📋 Шаги для запуска

### 1. Перейдите в директорию backend

```bash
cd backend
```

### 2. Активируйте виртуальное окружение

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Создайте миграции для новых полей

```bash
python manage.py makemigrations
```

Вы увидите, что будут созданы миграции для:
- Добавления поля `time_spent` в модель `Submission`
- Добавления поля `battle_end` в модель `BattleSettings`
- Изменения default для `battle_start` в модели `BattleSettings`

### 4. Примените миграции

```bash
python manage.py migrate
```

### 5. Запустите сервер

**Для разработки:**
```bash
python manage.py runserver
```

**Для продакшена (с поддержкой WebSocket):**
```bash
uvicorn sql_battle.asgi:application --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Доступные URL

После запуска сервера будут доступны:

- **API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/django-admin/
- **WebSocket**: ws://localhost:8000/ws/leaderboard/

---

## 🔍 Проверка работы

### 1. Проверьте настройки турнира

```bash
curl http://localhost:8000/api/admin/settings
```

Должны получить:
```json
{
  "battle_start": "2026-09-15T10:00:00+00:00",
  "battle_end": "2026-09-15T12:00:00+00:00",
  "round_duration_minutes": 120
}
```

### 2. Проверьте лидерборд

```bash
curl http://localhost:8000/api/leaderboard
```

Должны получить список пользователей с полем `total_time_spent` (суммарное время в секундах).

### 3. Проверьте профиль

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/profile/history
```

Должны получить историю решений с полем `time_spent`.

### 4. Проверьте WebSocket

Откройте браузер и выполните:
```javascript
const token = localStorage.getItem('sql_battle_token');
const ws = new WebSocket(`ws://localhost:8000/ws/leaderboard?token=${token}`);
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

---

## 📊 Новые возможности

### 1. Время пользователя (time_spent)
- Фронтенд отправляет время, потраченное на задачу
- Бэкенд сохраняет его в поле `time_spent`
- Лидерборд показывает суммарное время на все решенные задачи
- Профиль показывает время на каждую задачу

### 2. Настройки турнира
- `battle_start` - когда начинается турнир
- `battle_end` - когда заканчивается турнир
- Фронтенд использует эти данные для таймеров и блокировок

### 3. Завершение задачи
- Задача помечается как завершенная при нажатии "Отправить решение"
- Не зависит от правильности ответа
- Позволяет автоматически переходить к следующей задаче

### 4. Устойчивое сравнение результатов
- Обрабатывает разные типы данных (float vs int)
- Нормализует строки (регистр, пробелы)
- Обрабатывает JSON-строки
- Округляет float до 4 знаков

---

## 🐛 Возможные проблемы

### Проблема: "No migrations to apply"
**Решение:** Удалите базу данных и примените миграции заново:
```bash
rm db.sqlite3
python manage.py migrate
```

### Проблема: "Table api_submission has no column named time_spent"
**Решение:** Примените миграции:
```bash
python manage.py migrate
```

### Проблема: "WebSocket connection failed"
**Решение:** Убедитесь, что сервер запущен через uvicorn:
```bash
uvicorn sql_battle.asgi:application --reload
```

---

## 📚 Документация

- [SYNC_REPORT.md](SYNC_REPORT.md) - Подробный отчет о синхронизации
- [README.md](README.md) - Основная документация
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Руководство по установке
- [COMPLIANCE_REPORT.md](COMPLIANCE_REPORT.md) - Отчет о соответствии фронтенду

---

## ✅ Готово!

Бэкенд полностью синхронизирован с фронтендом и готов к использованию.

**Версия:** 2.0  
**Дата:** 11 сентября 2026  
**Статус:** ✅ Готово к продакшену
