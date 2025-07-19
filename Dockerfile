FROM ghcr.io/lavalink-devs/lavalink:4

# Install Python for the bot
RUN apt-get update \
    && apt-get install -y python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY bot.py ./
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Lavalink configuration
COPY lavalink/application.yml /opt/Lavalink/application.yml
COPY lavalink/plugins /opt/Lavalink/plugins
COPY lavalink/cookies.txt /opt/Lavalink/cookies.txt

CMD ["/app/entrypoint.sh"]
