# Используем официальный образ Python в качестве базового
FROM python:3.9-alpine

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["python", "bot.py"]