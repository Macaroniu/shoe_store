# Запуск

## Установка зависимостей
```bash
pip install -r source/requirements/requirements.txt
```

## Пуллим Python

```bash
docker pull python:3.11-slim
```

## Собираем образ

```bash
docker-compose build --no-cache
```

## Поднимаем контейнеры

```bash
docker-compose up
```

## Открываем UI

```bash
open source/frontend/index.html
```

# Все победка