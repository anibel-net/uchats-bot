import asyncio

from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import is_admin


@Client.on_message(filters.sticker, group=106)
async def on_sticker(client: Client, message: Message):
    if message.from_user:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received sticker'
                    f'from @{message.from_user.username} ({message.from_user.id}): {message.sticker.file_unique_id}')
        # </editor-fold>
        if await is_admin(client, message.chat.id, message.from_user.id):
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.info(f'[{message.chat.id} ({message.message_id})] user @{message.from_user.username} '
                        f'({message.from_user.id}) is administrator, ignoring.')
            # </editor-fold>
            return
    if message.sender_chat:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received sticker'
                    f'from @{message.sender_chat.username} ({message.sender_chat.id}): '
                    f'{message.sticker.file_unique_id}. Ignoring.')
        # </editor-fold>
        return
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Initialization chat_data...')
    # </editor-fold>
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] initialized.')
    logger.info(f'[{message.chat.id} ({message.message_id})] Checking sticker.')
    # </editor-fold>
    if message.sticker.file_unique_id in chat_data.banned_stickers:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Sticker {message.sticker.file_unique_id} banned. '
                    f'Deleting...')
        # </editor-fold>
        await message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Deleted.')
        # </editor-fold>
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>
    return


@Client.on_message(filters.command('ban sticker'), group=206)
async def on_ban_sticker(client: Client, message: Message):
    if message.from_user:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received message'
                    f'from @{message.from_user.username} ({message.from_user.id}): {message.text}')
        # </editor-fold>
        if not await is_admin(client, message.chat.id, message.from_user.id):
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.info(f'[{message.chat.id} ({message.message_id})] user @{message.from_user.username} '
                        f'({message.from_user.id}) isn\'t administrator, ignoring.')
            # </editor-fold>
            return
    if message.sender_chat:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received message'
                    f'from @{message.sender_chat.username} ({message.sender_chat.id}): {message.text}')
        # </editor-fold>

    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Initialization chat_data...')
    # </editor-fold>
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] initialized.')
    # </editor-fold>
    if message.reply_to_message.sticker is None:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Not reply. Reporting...')
        # </editor-fold>
        reply = await message.reply('Калі ласка, выкарыстоўвайце `/ban sticker у адказ на стыкер, які хочаце забаніць.')
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Reported. Sleeping...')
        # </editor-fold>
        await asyncio.sleep(10)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Deleting message and reply.')
        # </editor-fold>
        await message.delete()
        await reply.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return

    await chat_data.update('banned_stickers',
                           [*chat_data.banned_stickers, message.reply_to_message.sticker.file_unique_id])
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Added sticker to banned. Reporting...')
    # </editor-fold>
    reply = await message.reply(f'Стыкер паспяхова забанены (`{message.reply_to_message.sticker.file_unique_id}`).')
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Reported. Sleeping...')
    # </editor-fold>
    await asyncio.sleep(10)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Deleting message and reply.')
    # </editor-fold>
    await message.delete()
    await reply.delete()
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>
    return
