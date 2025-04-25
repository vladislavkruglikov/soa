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
    "login": "username7",
    "email": "username7@mail.ru",
    "password": "username7"
  }'
```

```bash
curl -X POST "http://localhost:8080/users/login" \
  -F "login=username6" \
  -F "password=username6"
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
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTQiLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDYyNjAyNjV9.YMg9a8TOucqM6_0wEm1kEsce3y5xg70UfUAUNUZ1zNc" \
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
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTUiLCJ1c2VyX2lkIjozLCJleHAiOjE3NDYyNjA1MjB9.xh65Z4k2rbuGqeEtJJtcz5r2nESis0dPpeTy3Erw9mI"
```

get post

```bash
curl -X GET "http://localhost:8080/posts/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTYiLCJ1c2VyX2lkIjo0LCJleHAiOjE3NDYyNjEzNTh9.8-pRbk3lox5C6pPGbooKSP4O-so3G0mOP3v2_Nr9kTM"
```

like post

```bash
curl -X POST "http://localhost:8080/posts/1/like" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTMiLCJ1c2VyX2lkIjoxLCJleHAiOjE3NDYyNjAzMDl9.nbpyIYg_3ghW6-6JFp44fMoN-OpAhVZHSz_cGEmKc8Q" \
  -H "Content-Type: application/json"
```

remove like

```bash
curl -X DELETE "http://localhost:8080/posts/1/like" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTQiLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDYyNjAyNjV9.YMg9a8TOucqM6_0wEm1kEsce3y5xg70UfUAUNUZ1zNc" \
  -H "Content-Type: application/json"
```

post comment

```bash
curl -X POST http://localhost:8080/posts/2/comments \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTYiLCJ1c2VyX2lkIjo0LCJleHAiOjE3NDYyNjE1MzB9.vVJQMdeg8Gc0B7ygjRcPIar3VrKy4lYB0t3-uKbw6cI" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a test comment"}'
```

get all comments
```bash
curl "http://localhost:8080/posts/1/comments?page=1&page_size=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTQiLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDYyNjAyNjV9.YMg9a8TOucqM6_0wEm1kEsce3y5xg70UfUAUNUZ1zNc"
```
