## ФИО

Кругликов Владислав Сергеевич

## Группа

БКНАД221

## Выбранный проект

Социальная сеть

## Полезные ссылки

Визуализация диаграм

* https://playground.likec4.dev
* https://dbdiagram.io

## Перед началом

```bash
./start.sh
```

+ запустить сервер и стрельнуть в него на создание пользователей чтобы таблицы завелись

## Запускаем

```bash
docker-compose up --build --force-recreate user_service gateway_service posts_service
```

todo: readiness probe на БД
todo: более гранулярно обновлять версию минорно

TODO: updated at = created at во время создания
TODO: добавить роль чтобы можно было менять данные у других пользоватлей

business rule: нельзя менять логин / пароль

pre condition созадвать бд новую для теста
TODO: добавить тесты на update
