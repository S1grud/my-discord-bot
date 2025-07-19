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
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Копируем остальной код
COPY . /app

WORKDIR /app

RUN chmod +x /app/entrypoint.sh

EXPOSE 2333

CMD ["/app/entrypoint.sh"]
