from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import is_admin


@Client.on_message(filters.command('rules'))
async def new_chat_member_handler(_: Client, message: Message):
    if message.from_user:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Received message'
                     f'from @{message.from_user.username} ({message.from_user.id}): {message.text}')
        # </editor-fold>
    if message.sender_chat:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Received message'
                     f'from @{message.sender_chat.username} ({message.sender_chat.id}): {message.text}')
        # </editor-fold>
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Initialization chat_data...')
    # </editor-fold>
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] initialized.')
    # </editor-fold>
    await message.reply(chat_data.rules)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Sent rules. Done.')
    # </editor-fold>
    return


@Client.on_message(filters.command('set rules'))
async def set_command_handler(client: Client, message: Message):
    if message.from_user:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Received message'
                     f'from @{message.from_user.username} ({message.from_user.id}): {message.text}')
        # </editor-fold>
        if not await is_admin(client, message.chat.id, message.from_user.id):
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] user @{message.from_user.username} '
                         f'({message.from_user.id}) isn\'t administrator, ignoring.')
            # </editor-fold>
            return
    if message.sender_chat:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Received message'
                     f'from @{message.sender_chat.username} ({message.sender_chat.id}): {message.text}')
        # </editor-fold>

    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Initialization chat_data...')
    # </editor-fold>
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] initialized.')
    logger.debug(f'[{message.chat.id} ({message.message_id})] Changing rules.')
    # </editor-fold>
    logger.info(message.command[0])
    await chat_data.update('rules', ' '.join(message.command[1:]))
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Changed rules; reporting.')
    # </editor-fold>
    await message.reply('Правілы паспяхова зменены!')
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>
