from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, ChatPermissions


@Client.on_message(~filters.service, group=709)
async def on_any_message(client: Client, message: Message):
    if (message.sender_chat and message.sender_chat.id == message.chat.id) or message.reply_to_message:
        return
    try:
        await client.get_chat_member(message.chat.id, message.from_user.id)
    except UserNotParticipant:
        await message.delete()
        await client.restrict_chat_member(message.chat.id, message.from_user.id,
                                          ChatPermissions(can_send_messages=False))
