import os

from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import admin_filter


@Client.on_message(filters.command(['rules', f'rules@{os.environ.get("BOT_USERNAME")}']), group=302)
async def on_rules(_: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await message.reply(chat_data.rules)
    return


@Client.on_message(filters.command('set rules') & admin_filter, group=202)
async def on_set_rules(message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('rules', message.text.markdown[11:])
    await message.reply('Правілы паспяхова зменены!')
