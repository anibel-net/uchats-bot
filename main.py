import os

from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

if __name__ == '__main__':
    app = Client(':memory:', os.environ.get('API_ID'), os.environ.get('API_HASH'),
                 bot_token=os.environ.get('BOT_TOKEN'), plugins=dict(root='handlers'))
    app.run()
