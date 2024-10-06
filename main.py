import os
import discord
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import asyncio

# Load the .env file
load_dotenv()

# Get environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Store the latest video ID to avoid spamming
last_video_id = None

async def check_for_new_video():
    global last_video_id

    try:
        # Call the YouTube API to get the latest video from the channel
        response = youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            order="date",
            type="video",
            maxResults=1
        ).execute()

        # Get the latest video ID
        latest_video = response['items'][0]
        latest_video_id = latest_video['id']['videoId']
        video_title = latest_video['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={latest_video_id}"

        # If it's a new video, send a message to the Discord channel
        if latest_video_id != last_video_id:
            last_video_id = latest_video_id
            channel = bot.get_channel(CHANNEL_ID)

            if channel:
                await channel.send(f"@everyone, a new video is up! 🎥\n**{video_title}**\n{video_url}")
        else:
            print("No new video found.")

    except HttpError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Background task that checks for new videos every 5 minutes
async def background_task():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await check_for_new_video()
        await asyncio.sleep(300)  # 5 minutes

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(background_task())  # Start the background task

# Start the bot
bot.run(DISCORD_TOKEN)
