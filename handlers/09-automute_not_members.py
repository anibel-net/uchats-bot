from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, ChatPermissions

from db.ChatData import ChatData
from functions import admin_filter


@Client.on_message(~filters.service & ~admin_filter, group=709)
async def on_any_message(client: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    if message.sender_chat.id in chat_data.whitelisted_channels:
        return
    try:
        await client.get_chat_member(message.chat.id, message.from_user.id)
    except UserNotParticipant:
        await message.delete()
        await client.restrict_chat_member(message.chat.id, message.from_user.id,
                                          ChatPermissions(can_send_messages=False))
