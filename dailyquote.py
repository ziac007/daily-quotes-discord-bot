import discord
from discord.ext import tasks, commands
import requests
import pytz
from datetime import datetime
import os
from dotenv import load_dotenv
from keepalive import keep_alive


load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_sent_date = None

def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        response.raise_for_status()
        json_data = response.json()
        quote = f'"{json_data[0]["q"]}" — {json_data[0]["a"]}'
        return quote
    except Exception as e:
        print(f"[ERROR] Failed to fetch quote: {e}")
        return "Could not fetch quote today."

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    schedule_daily_quote.start()

@tasks.loop(minutes=1)
async def schedule_daily_quote():
    global last_sent_date
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    if now.hour == 17 and now.minute in (25, 26):
        today = now.date()
        if last_sent_date != today:
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                quote = get_quote()
                await channel.send(quote)
                print(f"[INFO] Quote sent at {now.strftime('%H:%M:%S')}")
                last_sent_date = today
            else:
                print(f"[ERROR] Channel with ID {CHANNEL_ID} not found.")

keep_alive()
bot.run(TOKEN)
