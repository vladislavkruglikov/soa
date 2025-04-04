# API Gateway

Зоны ответственности:
- Принимать запросы от фронтенда (UI).
- Перенаправлять запросы в нужный сервис (User Service, Stats Service, Posts Service).
- Формировать единый REST API для внешнего взаимодействия.

Границы сервиса:
- Не хранит бизнес-логику.
- Не обрабатывает данные самостоятельно, только маршрутизация и базовая валидация.
- Сервис не имеет собственной БД

# Примеры запросов

Создать пользователя

```bash
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser1",
    "email": "1test@example.com",
    "password": "secret123"
  }'
```

```bash
curl -X POST "http://localhost:8080/users/login" \
  -F "login=testuser1" \
  -F "password=secret123"
```

<!-- eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjEiLCJleHAiOjE3NDM3ODg3NjZ9.d6dIKv0Ybrhn2SqxTiZ2SxuTqVe3DcQ8ccrxidKT-sc -->

try without auth bearer / correct / wrong

```bash
curl -X POST "http://localhost:8080/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 11111" \
  -d '{
    "title": "Test Post",
    "description": "This is a test post created via proxy.",
    "is_private": false,
    "tags": ["tag1", "tag2"]
  }'
```

```bash
curl -X POST "http://localhost:8080/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjEiLCJ1c2VyX2lkIjoxLCJleHAiOjE3NDM3ODk1MzB9.yJJ7xYhfKJxJuWYamA8XnWxGC28TSg9D62ULoFLV7ks" \
  -d '{
    "title": "Test Post",
    "description": "This is a test post created via proxy.",
    "is_private": false,
    "tags": ["tag1", "tag2"]
  }'
```

```bash
curl -X GET "http://localhost:8080/posts?page_number=1&page_size=10" \
  -H "Authorization: Bearer 123"
```

```bash
curl -X GET "http://localhost:8080/posts?page_number=1&page_size=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjEiLCJ1c2VyX2lkIjoxLCJleHAiOjE3NDM3ODk1MzB9.yJJ7xYhfKJxJuWYamA8XnWxGC28TSg9D62ULoFLV7ks"
```
