import discord
from discord.ext import tasks, commands
import requests
import pytz
from datetime import datetime
import os
from dotenv import load_dotenv

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
    
    #Specify your time here
    if now.hour == 7 and now.minute in (0, 1):
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

bot.run(TOKEN)