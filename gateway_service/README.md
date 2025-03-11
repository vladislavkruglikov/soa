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
    "login": "testuser",
    "email": "test@example.com",
    "password": "secret123"
  }'
```
