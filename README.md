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
docker-compose up --build --force-recreate zookeeper kafka kafka-ui
docker-compose up --build --force-recreate user_service gateway_service posts_service stats_service
```

todo: readiness probe на БД
todo: более гранулярно обновлять версию минорно

TODO: updated at = created at во время создания
TODO: добавить роль чтобы можно было менять данные у других пользоватлей

business rule: нельзя менять логин / пароль

pre condition созадвать бд новую для теста
TODO: добавить тесты на update

## https://habr.com/ru/articles/753398/

http://localhost:8082

Cluster name - Можете указать просто как "Kafka Cluster"
Bootstrap Servers - Суда вам внужно вписать PLAINTEXT://kafka:29092
metrics type -> JMX
metrics type -> JMX
port -> 9092


todo: дописать в gateway прокидывание ошибки
