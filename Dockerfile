FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей и установка
COPY source/requirements/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Копирование исходного кода (ИСПРАВЛЕНО)
# У вас структура: src/ (не source/src/)
COPY ./source/src ./src
COPY ./static ./static

# Создание директорий для статики
RUN mkdir -p /app/static/images && \
    chmod -R 755 /app/static

# Порт приложения
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "src.entrypoints.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]