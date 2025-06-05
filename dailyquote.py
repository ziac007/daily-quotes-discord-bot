import discord
from discord.ext import tasks, commands
import requests
import pytz
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

last_sent_date = None

# Get a quote from API
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

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    schedule_daily_quote.start()

# Task loop for sending daily quote
@tasks.loop(minutes=1)
async def schedule_daily_quote():
    global last_sent_date
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    if now.hour == 6 and now.minute in (0, 1):  # 6:00–6:01 AM IST
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

# Flask keep-alive server
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Start everything
keep_alive()
bot.run(TOKEN)