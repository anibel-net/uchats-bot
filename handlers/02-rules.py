import os

from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import is_admin


@Client.on_message(filters.command(['rules', f'rules@{os.environ.get("BOT_USERNAME")}']), group=302)
async def on_rules(_: Client, message: Message):
    if message.from_user:
        ...
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        ...
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await message.reply(chat_data.rules)
    return


@Client.on_message(filters.command('set rules'), group=202)
async def on_set_rules(client: Client, message: Message):
    if message.from_user:
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        ...

    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('rules', message.text.markdown[11:])
    await message.reply('Правілы паспяхова зменены!')
