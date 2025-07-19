FROM debian:bookworm-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless python3 python3-pip wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Скачиваем Lavalink
RUN mkdir -p /opt/Lavalink && \
    wget -O /opt/Lavalink/Lavalink.jar https://github.com/freyacodes/Lavalink/releases/download/4.0.0/Lavalink.jar

# Копируем requirements.txt и ставим зависимости Python
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . /app

# Указываем рабочую директорию
WORKDIR /app

# Делаем entrypoint.sh исполняемым
RUN chmod +x /app/entrypoint.sh

# Открываем порт Lavalink (2333)
EXPOSE 2333

# Запуск обоих сервисов
CMD ["/app/entrypoint.sh"]
