# User Service

Зоны ответственности:
- Регистрация и аутентификация пользователей.
- Хранение и управление информацией о пользователях и их ролях.
- Проверка прав доступа.

Границы сервиса:
- Отвечает только за пользователей и их данные.
- Предоставляет API для регистрации, входа в систему, обновления профиля.
- Не обрабатывает статистику, лайки, посты, комментарии.

# Примеры запросов

Создать пользователя

```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "email": "test@example.com",
    "password": "secret123"
  }'
```

Аутентификация получения JWT токена

```bash
curl -X POST "http://localhost:8000/users/login" \
  -F "login=testuser" \
  -F "password=secret123"
```

Получение данных профиля

```bash
curl -X GET "http://localhost:8000/users/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmczIiwiZXhwIjoxNzQyNTcxMTU1fQ.zkgsKwmdf-OfhDkO2_lckxB7z1CPLBqiAruKPXR-lto"
```

Обновление профиля

```bash
curl -X PUT "http://localhost:8000/users/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0MTcyMjUyNH0.0XdtUfq0MOPT9cMKnTSEyc8jN3jsKgunfG5_Hmnunzs" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-01-01",
    "phone": "1234567890",
    "email": "john.doe@example.com"
  }'
```

# Тесты

Запуск

```bash
docker-compose up --build tests
```
