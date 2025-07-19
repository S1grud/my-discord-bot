#!/bin/bash
set -e
java -jar /opt/Lavalink/Lavalink.jar &

exec python3 /app/bot.py
