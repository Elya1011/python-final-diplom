# Docker Инструкции для запуска приложения

## Файлы созданы:
- `Dockerfile` - конфигурация для сборки образа Django приложения
- `docker-compose.yml` - оркестрация сервисов (Django, PostgreSQL, Redis, Celery)
- `.dockerignore` - исключения из Docker образа
- Обновленный `requirements.txt` с production зависимостями

## Как запустить:

### 1. Сборка и запуск всех сервисов:
```bash
docker-compose up --build
```

### 2. Запуск в фоновом режиме:
```bash
docker-compose up --build -d
```

### 3. Остановка сервисов:
```bash
docker-compose down
```

### 4. Просмотр логов:
```bash
docker-compose logs -f web
docker-compose logs -f celery
```

## Доступные сервисы:
- **Web приложение**: http://localhost:8000
- **Redis**: localhost:6379

## Полезные команды:

### Создание суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Применение миграций:
```bash
docker-compose exec web python manage.py migrate
```

### Сборка статических файлов:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Вход в контейнер:
```bash
docker-compose exec web bash
```

## Структура сервисов:
- **web**: Django приложение с Gunicorn
- **redis**: Redis для Celery
- **celery**: Worker для фоновых задач
- **celery-beat**: Планировщик задач
