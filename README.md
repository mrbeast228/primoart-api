# PrimoART API
Хранит мониторинговые данные по проектам, сервисам и транзакциям для их дальнейшего анализа и обработки на стороне front server

## Структура
Схема данных - https://wiki.yandex.ru/homepage/mon/internal/active/primoart

## Документация
Упакована в Swagger Docs (TODO добавить примеры response на SDR)

## Использование
```shell
# Запустите контейнер
sudo docker compose up &

# Сгенерируйте фейковые данные
sudo docker exec -it uvicorn-api /usr/local/bin/python3 -m mvp.generator

# Default endpoint is 0.0.0.0:8000
```
