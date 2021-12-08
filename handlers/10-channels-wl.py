import time

from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import validate_channel


@Client.on_message(filters.create(lambda _, __, message: message.sender_chat is not None), group=110)
async def on_message_from_chat(_: Client, message: Message):
    if message.sender_chat.id == message.chat.id:
        return
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    if message.sender_chat.id in chat_data.whitelisted_channels:
        return
    await message.delete()
    await message.chat.kick_member(message.sender_chat.id, int(time.time()) + 600)


@Client.on_message(filters.command('wl') & filters.admin)
async def on_wl(client: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('whitelisted_channels', [
        *chat_data.whitelisted_channels,
        *[channel['id'] for channel in filter(None, [await validate_channel(client, s) for s in message.command[1:]])]
    ])
    await message.reply('Каналы дазволены')


@Client.on_message(filters.command('un_wl') & filters.admin)
async def on_un_wl(client: Client, message: Message):
    channels: list[int] = \
        [channel['id'] for channel in filter(None, [await validate_channel(client, s) for s in message.command[1:]])]
    if message.reply_to_message and message.reply_to_message.sender_chat:
        channels.append(message.reply_to_message.sender_chat.id)
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('whitelisted_channels', list(set(chat_data.whitelisted_channels) - set(channels)))
    await message.reply('Каналы забаронены')
