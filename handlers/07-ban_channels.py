import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import ParsedChannel, validate_channel


@Client.on_message(filters.forwarded & ~filters.admin, group=107)
async def on_forward(_: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    if message.forward_from_chat.id in chat_data.banned_channels:
        await message.delete()
    return


@Client.on_message(filters.regex(r'(?P<url>t.me/[^\s]+)') & ~filters.admin, group=107)
async def on_link(client: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    for match in message.matches:
        chat = await client.get_chat(match.group('url').split('/')[1])
        if chat.id in chat_data.banned_channels:
            await message.delete()


@Client.on_message(filters.command('ban channel') & filters.admin, group=207)
async def on_ban_channel(client: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    if len(message.command) == 1 and \
            (message.reply_to_message is None
             or message.reply_to_message.forward_from_chat is None
             or message.reply_to_message.forward_from_chat.type != 'channel'):
        reply = await message.reply('Калі ласка, выкарыстоўвайце `/ban channel @username` '
                                    'ці `/ban channel id` альбо дашліце гэтае паведамленне '
                                    'ў адказ на перадасланы пост з канала, які хочаце забаніць.')
        await asyncio.sleep(10)
        await message.delete()
        await reply.delete()
        return

    ban_candidates: list[ParsedChannel] = []

    if message.reply_to_message and message.reply_to_message.forward_from_chat \
            and message.reply_to_message.forward_from_chat.type == 'channel':
        ban_candidates.append({
            'id': message.reply_to_message.forward_from_chat.id,
            'username': message.reply_to_message.forward_from_chat.username,
            'title': str(message.reply_to_message.forward_from_chat.title)
        })

    if len(message.command) > 1:
        for arg in message.command[1:]:
            channel = await validate_channel(client, arg)
            if channel:
                ban_candidates.append(channel)

    await chat_data.update('banned_channels', [*chat_data.banned_channels, *[i['id'] for i in ban_candidates]])
    reply = await message.reply('Паспяхова забанены каналы: {channels_list}.'.format(
        channels_list=", ".join([chat["title"] for chat in ban_candidates])
    ))
    await asyncio.sleep(10)
    await message.delete()
    await reply.delete()
    return
