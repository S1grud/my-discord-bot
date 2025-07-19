# Simple Discord Bot

This bot responds with random memes and ChatGPT-powered answers. It runs without any music features or Lavalink dependencies.

## Running on Koyeb

1. Build the Docker image:
   ```bash
   docker build -t my-discord-bot .
   ```
2. Push the image to a container registry.
3. Deploy the image on Koyeb using a Docker deployment so the bot remains online.

The bot expects the environment variables `OPENAI_API_KEY` and `DISCORD_BOT_TOKEN` to be provided.
