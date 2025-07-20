import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
import openai
import os
from dotenv import load_dotenv
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

def run_http_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

    server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()


# load keys
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# check if keys exist
if not OPENAI_KEY or not DISCORD_TOKEN:
    print("Ошибка: Убедитесь, что вы создали .env файл с OPENAI_API_KEY и DISCORD_BOT_TOKEN")
    exit()

# openAI
openai_client = openai.AsyncOpenAI(api_key=OPENAI_KEY)

# intents discord
myintents = discord.Intents.default()
myintents.message_content = True

botie = commands.Bot(command_prefix='$', intents=myintents)

# functions
def get_meme():
  try:
    response = requests.get('https://meme-api.com/gimme')
    response.raise_for_status() # check for errors
    json_data = json.loads(response.text)
    return json_data['url']
  except requests.exceptions.RequestException as e:
    print(f"Ошибка при запросе к meme-api: {e}")
    return "Не удалось загрузить мем, попробуйте позже."

# bot events
@botie.event
async def on_ready():
  print(f'Bot {botie.user} ready to work!')

  await botie.tree.sync(guild=discord.Object(id=1090677113767604307))
  print("Слэш-команды синхронизированы.")

# bot commands (with / hints)

  # random meme
@botie.tree.command(name="meme", description="Получить случайный мем с Reddit")
async def meme_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    meme_url = get_meme()
    await interaction.followup.send(meme_url)

  # chatgpt khata
@botie.tree.command(name="khata", description="Получить совет по тюряге")
async def khata_slash(interaction: discord.Interaction, prompt: str = None):
    await interaction.response.defer()
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Ты — дискорд-бот, который сидит на зоне. Рассказываешь новичкам, как входить в хату"},
                {"role": "user", "content": "Дай один краткий случайный совет как входить в хату или как жить по масти."}
            ],
            max_tokens=1500
        )
        answer = response.choices[0].message.content
        await interaction.followup.send(answer)
    except Exception as e:
        print(f"Произошла ошибка при обращении к OpenAI API: {e}")
        await interaction.followup.send("Извините, не могу ответить на ваш вопрос прямо сейчас. Попробуйте позже.")

  # chatgpt ask (anything)
@botie.tree.command(name="askgpt", description="Задать любой вопрос ChatGPT")
@app_commands.describe(prompt="Текст вашего вопроса")
async def askgpt_slash(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Ты — дискорд-бот, который отвечает на вопросы пользователей."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000
        )
        answer = response.choices[0].message.content
        await interaction.followup.send(answer)
    except Exception as e:
        print(f"Произошла ошибка при обращении к OpenAI API: {e}")
        await interaction.followup.send("Извините, не могу ответить на ваш вопрос прямо сейчас. Попробуйте позже.")

# run bot
botie.run(DISCORD_TOKEN)
