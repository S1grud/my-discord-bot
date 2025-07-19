import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
import openai
import os
from dotenv import load_dotenv
import wavelink

# load keys
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")
LAVALINK_URI = os.getenv("LAVALINK_URI", "http://localhost:2333")

# check if keys exist
if not OPENAI_KEY or not DISCORD_TOKEN or not LAVALINK_PASSWORD:
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
  
  node = wavelink.Node(uri=LAVALINK_URI, password=LAVALINK_PASSWORD)
  await wavelink.Pool.connect(nodes=[node], client=botie)
  

@botie.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"Узел Wavelink {payload.node.identifier} готов.")

@botie.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    player: wavelink.Player = payload.player
    
    if player.queue.is_empty:
        return

    next_track = player.queue.get()

    await player.play(next_track)

    if hasattr(player, "home") and player.home:
        await player.home.send(f"▶️ Включаю: **{next_track.title}**")

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

  # music
@botie.tree.command(name="play", description="Включить музыку по названию или ссылке")
@app_commands.describe(search="Название трека или ссылка на YouTube")
async def play_slash(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Вы должны быть в голосовом канале, чтобы включить музыку.", ephemeral=True)
        return

    await interaction.response.defer()

    player: wavelink.Player
    if not interaction.guild.voice_client:
        player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
    else:
        player = interaction.guild.voice_client

    if not hasattr(player, "home"):
        player.home = interaction.channel
    elif player.home is None:
        player.home = interaction.channel

    try:
        tracks: list[wavelink.Playable] = await wavelink.Playable.search(search)
        if not tracks:
            await interaction.followup.send(f"Не удалось найти треки по запросу: `{search}`")
            return
    except Exception as e:
        await interaction.followup.send(f"Произошла ошибка при поиске трека: {e}")
        return

    track = tracks[0]

    if player.playing:
        await player.queue.put_wait(track)
        await interaction.followup.send(f"Добавил в очередь: **{track.title}**")
    else:
        await player.play(track, populate=True)
        await interaction.followup.send(f"▶️ Включаю: **{track.title}**")

@botie.tree.command(name="leave", description="Остановить и отключить бота")
async def disconnect_slash(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if player:
        player.queue.clear()
        await player.stop()
        await player.disconnect()
        await interaction.response.send_message("Отключился от голосового канала.")
    else:
        await interaction.response.send_message("Я не нахожусь в голосовом канале.", ephemeral=True)

@botie.tree.command(name="pause", description="Поставить текущую песню на паузу")
async def pause_slash(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if not player or not player.playing:
        await interaction.response.send_message("Сейчас ничего не играет.", ephemeral=True)
        return

    if player.paused:
        await interaction.response.send_message("Песня уже на паузе!", ephemeral=True)
        return

    await player.pause(True)
    await interaction.response.send_message("⏸️ Песня поставлена на паузу.")

@botie.tree.command(name="resume", description="Продолжить воспроизведение песни")
async def resume_slash(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if not player:
        await interaction.response.send_message("Бот не в голосовом канале.", ephemeral=True)
        return
        
    if not player.paused:
        await interaction.response.send_message("Воспроизведение и так активно!", ephemeral=True)
        return

    await player.pause(False)
    await interaction.response.send_message("▶️ Воспроизведение продолжено.")

@botie.tree.command(name="next", description="Переключить на следующую песню в очереди")
async def next_slash(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if not player or not player.playing:
        await interaction.response.send_message("Сейчас ничего не играет, чтобы можно было переключить.", ephemeral=True)
        return

    if player.queue.is_empty:
        await interaction.response.send_message("Очередь пуста, больше песен нет!", ephemeral=True)
        return

    await player.stop()
    await interaction.response.send_message("⏭️ Переключаю на следующую песню...")

# run bot
botie.run(DISCORD_TOKEN)