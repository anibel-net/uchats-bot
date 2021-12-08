import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData


@Client.on_message(filters.sticker & ~filters.admin, group=106)
async def on_sticker(_: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    if message.sticker.file_unique_id in chat_data.banned_stickers:
        await message.delete()
    if message.sticker.set_name in chat_data.banned_stickerpacks:
        await message.delete()
    return


@Client.on_message(filters.command('ban sticker') & filters.admin, group=206)
async def on_ban_sticker(_: Client, message: Message):
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


@Client.on_message(filters.command('ban stickerpack') & filters.admin, group=206)
async def on_ban_stickerpack(_: Client, message: Message):

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
