import os

from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
import requests

load_dotenv()

if __name__ == '__main__':
    app = Client(':memory:', os.environ.get('API_ID'), os.environ.get('API_HASH'),
                 bot_token=os.environ.get('BOT_TOKEN'), plugins=dict(root='handlers'))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: requests.get(os.environ.get('HEARTBEAT_URL')), 'interval', minutes=1)
    scheduler.start()
    app.run()
