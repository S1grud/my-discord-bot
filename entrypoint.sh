#!/bin/bash
set -e
java -jar /opt/Lavalink/Lavalink.jar &
python3 /app/bot.py
