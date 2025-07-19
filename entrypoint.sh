#!/bin/bash
set -e

java -jar /opt/Lavalink/Lavalink.jar &

echo "Wait for Lavalink to start..."
sleep 30  # можно увеличить если всё равно не хватает

exec python3 /app/bot.py
