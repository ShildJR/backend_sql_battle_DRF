# 🚀 Инструкция по запуску SQL Battle Backend

## ✅ Проблема решена!

Синтаксическая ошибка в `views.py` исправлена. Теперь проект готов к запуску.

## 📋 Шаги для запуска

### 1. Перейдите в директорию backend

```bash
cd backend
```

### 2. Создайте виртуальное окружение (если еще не создано)

```bash
python -m venv venv
```

### 3. Активируйте виртуальное окружение

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Установите зависимости

```bash
pip install -r requirements.txt
```

### 5. Создайте миграции

```bash
python manage.py makemigrations
```

### 6. Примените миграции

```bash
python manage.py migrate
```

### 7. Создайте администратора

```bash
python manage.py create_admin
```

Следуйте инструкциям:
- Введите имя пользователя (например: `admin`)
- Введите email (например: `admin@example.com`)
- Введите пароль (например: `admin123`)

### 8. Загрузите тестовые задачи (опционально)

```bash
python manage.py loaddata api/fixtures/tasks.json
```

### 9. Запустите сервер разработки

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: **http://localhost:8000**

## 🌐 Доступные URL

- **API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/django-admin/
- **WebSocket**: ws://localhost:8000/ws/leaderboard/

## 🔍 Проверка работы

### Проверьте API

```bash
# Получение списка задач
curl http://localhost:8000/api/tasks

# Вход в систему
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Проверьте Django Admin

1. Откройте http://localhost:8000/django-admin/
2. Войдите с учетными данными администратора
3. Вы должны увидеть:
   - Users (пользователи)
   - Tasks (задачи)
   - Task Assignments (назначения задач)
   - User Groups (группы пользователей)
   - Battle Settings (настройки)

## 📚 Документация

- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт
- [README.md](README.md) - Основная документация
- [COMPLIANCE_REPORT.md](COMPLIANCE_REPORT.md) - Отчет о соответствии фронтенду
- [DJANGO_ADMIN_GUIDE.md](DJANGO_ADMIN_GUIDE.md) - Руководство по Django Admin
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Итоговый отчет о проекте

## 🎯 Основные возможности

### Для участников:
- Регистрация и вход
- Просмотр задач
- Выполнение SQL запросов
- Отправка решений
- Просмотр профиля и истории
- Таблица лидеров (в реальном времени)

### Для администраторов:
- Управление пользователями
- Создание и редактирование задач
- Массовое назначение задач
- Управление группами пользователей
- Настройка параметров системы

## 🔧 Возможные проблемы

### Проблема: "No module named 'django'"
**Решение**: Убедитесь, что активировали виртуальное окружение и установили зависимости:
```bash
pip install -r requirements.txt
```

### Проблема: "Table does not exist"
**Решение**: Примените миграции:
```bash
python manage.py migrate
```

### Проблема: "Permission denied"
**Решение**: Убедитесь, что у вас есть права на запись в директорию проекта.

## ✨ Готово!

Теперь ваш бэкенд полностью настроен и готов к работе с фронтендом SQL Battle!

---

**Версия**: 1.0
**Дата**: Сентябрь 2026
**Статус**: ✅ Готово к использованию
