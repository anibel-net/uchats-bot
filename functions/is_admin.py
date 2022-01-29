import os

from pyrogram import filters
from pyrogram.types import Message


async def is_admin(_, __, message: Message):
    return (message.sender_chat and message.sender_chat.id == message.chat.id) or \
           (message.from_user and (
                   (await message.chat.get_member(message.from_user.id)).status in ('creator', 'administrator')) or
            message.from_user.id in [int(uid) for uid in os.getenv('ADMINS').split(';')]
            )


admin_filter = filters.create(is_admin)
