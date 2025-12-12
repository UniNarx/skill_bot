# Используем легкий Python 3.10
FROM python:3.10-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта внутрь
COPY . .

# Запускаем бота
CMD ["python", "main.py"]