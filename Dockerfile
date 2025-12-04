FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY source/requirements/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./source/src ./src
COPY ./static ./static

RUN mkdir -p /app/static/images && \
    chmod -R 755 /app/static

EXPOSE 8000

CMD ["uvicorn", "src.entrypoints.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]