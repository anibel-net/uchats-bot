import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import is_admin


@Client.on_message(filters.sticker, group=106)
async def on_sticker(client: Client, message: Message):
    if message.from_user:
        if await is_admin(client, message.chat.id, message.from_user.id):
            return
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    if message.sticker.file_unique_id in chat_data.banned_stickers:
        await message.delete()
    if message.sticker.set_name in chat_data.banned_stickerpacks:
        await message.delete()
    return


@Client.on_message(filters.command('ban sticker'), group=206)
async def on_ban_sticker(client: Client, message: Message):
    if message.from_user:
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        ...

    if message.reply_to_message.sticker is None:
        reply = await message.reply('Калі ласка, выкарыстоўвайце `/ban sticker у адказ на стыкер, які хочаце забаніць.')
        await asyncio.sleep(10)
        await message.delete()
        await reply.delete()
        return

    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('banned_stickers',
                           [*chat_data.banned_stickers, message.reply_to_message.sticker.file_unique_id])
    reply = await message.reply(f'Стыкер паспяхова забанены (`{message.reply_to_message.sticker.file_unique_id}`).')
    await asyncio.sleep(10)
    await message.delete()
    await reply.delete()
    return


@Client.on_message(filters.command('ban stickerpack'), group=206)
async def on_ban_stickerpack(client: Client, message: Message):
    if message.from_user:
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return
    if message.sender_chat:
        ...

    if message.reply_to_message.sticker is None:
        reply = await message.reply(
            'Калі ласка, выкарыстоўвайце `/ban stickerpack у адказ на стыкер, які хочаце забаніць.')
        await asyncio.sleep(10)
        await message.delete()
        await reply.delete()
        return

    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('banned_stickerpacks',
                           [*chat_data.banned_stickerpacks, message.reply_to_message.sticker.set_name])
    reply = await message.reply(f'Стыкерпак паспяхова забанены (`{message.reply_to_message.sticker.set_name}`).')
    await asyncio.sleep(10)
    await message.delete()
    await reply.delete()
    return
