from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import UserNotParticipant


@Client.on_message(~filters.service, group=709)
async def on_any_message(client: Client, message: Message):
    if message.sender_chat or message.reply_to_message:
        return
    try:
        await client.get_chat_member(message.chat.id, message.from_user.id)
    except UserNotParticipant:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received message not from chat member.')
        logger.info(f'[{message.chat.id} ({message.message_id})] Deleting message...')
        # </editor-fold>
        await message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Message deleted.')
        logger.info(f'[{message.chat.id} ({message.message_id})] Restricting user...')
        # </editor-fold>
        await client.restrict_chat_member(message.chat.id, message.from_user.id,
                                          ChatPermissions(can_send_messages=False))
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Restricted user.')
        logger.info(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>