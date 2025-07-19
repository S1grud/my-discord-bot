#!/bin/bash
set -e

# Запускаем Lavalink в фоне
java -jar /opt/Lavalink/Lavalink.jar &

# Ждем несколько секунд, чтобы Lavalink стартовал
sleep 10

# Запускаем Discord-бота (Python)
exec python3 /app/bot.py
