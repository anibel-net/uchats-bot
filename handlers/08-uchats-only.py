from loguru import logger
from pyrogram import Client
from pyrogram.types import Message


@Client.on_message(group=708)
def on_message(_: Client, message: Message):
    if message.chat.id != -1001322065959:
        message.chat.leave()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Left chat.')
        # </editor-fold>
    return
