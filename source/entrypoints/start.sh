#!/bin/bash

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  🚀 Запуск приложения 'ООО Обувь'"
echo "========================================"
echo ""

# Определяем корень проекта (где находится docker-compose.yml)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Если скрипт в source/entrypoints/, поднимаемся на 2 уровня вверх
if [[ "$SCRIPT_DIR" == */source/entrypoints ]]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
fi

cd "$PROJECT_ROOT" || exit 1
echo -e "${BLUE}📁 Корень проекта: $(pwd)${NC}"
echo ""

# Проверка файла app.py
APP_FILE="source/frontend/app.py"
if [ ! -f "$APP_FILE" ]; then
    echo -e "${RED}❌ Файл не найден: $APP_FILE${NC}"
    echo ""
    echo "Доступные файлы:"
    find . -name "app.py" -type f 2>/dev/null
    exit 1
fi
echo -e "${GREEN}✅ Найден файл: $APP_FILE${NC}"
echo ""

# Проверка Docker
echo -e "${BLUE}[1/4]${NC} Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker найден${NC}"

# Запуск Docker Compose
echo ""
echo -e "${BLUE}[2/4]${NC} Запуск backend через Docker..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка запуска Docker${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend запущен${NC}"

# Ожидание и проверка API
echo ""
echo -e "${BLUE}[3/4]${NC} Ожидание готовности API..."
for i in {20..1}; do
    echo -ne "${YELLOW}⏳ $i секунд...${NC}\r"
    sleep 1
done
echo ""

# Проверка доступности API
echo -ne "${YELLOW}Проверка API...${NC}"
for i in {1..5}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "\r${GREEN}✅ API готов к работе!          ${NC}"
        break
    fi
    sleep 2
    echo -ne "\r${YELLOW}Проверка API... попытка $i/5${NC}"
done
echo ""

# Проверка зависимостей
echo ""
echo -e "${BLUE}[4/4]${NC} Проверка зависимостей..."
python3 -c "import customtkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Устанавливаю зависимости...${NC}"
    pip3 install -q customtkinter pillow requests
fi
echo -e "${GREEN}✅ Зависимости установлены${NC}"

# Запуск приложения
echo ""
echo "========================================"
echo "  ✨ Запуск desktop приложения..."
echo "========================================"
echo ""
echo "📊 Backend: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}🚀 Запуск: python3 $APP_FILE${NC}"
echo ""

python3 "$APP_FILE"

# Остановка Docker
echo ""
echo "========================================"
read -p "Остановить Docker? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    echo -e "${GREEN}✅ Docker остановлен${NC}"
fi

echo ""
echo "Готово! 👋"