import asyncio

from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message

from db.ChatData import ChatData
from functions import is_admin


@Client.on_message(filters.new_chat_members | filters.command('test welcome'))
async def new_chat_member_handler(client: Client, message: Message):
    if not message.service:
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
    else:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] New user joined chat: '
                     + ', '.join(map(lambda user: f'@{user.username} ({user.id})', message.new_chat_members)))
        # </editor-fold>
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Initialization chat_data...')
    # </editor-fold>
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] initialized.')
    # </editor-fold>
    if message.new_chat_members:
        replied = [await message.reply(chat_data.welcome_message.format(**user.__dict__))
                   for user in message.new_chat_members]
    else:
        replied = [await message.reply(chat_data.welcome_message.format(
            **message.from_user.__dict__ if message.from_user else message.sender_chat.__dict__))]
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Sent all welcome messages; waiting.')
    # </editor-fold>
    await asyncio.sleep(chat_data.welcome_message_timeout)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Deleting all welcome messages.')
    # </editor-fold>
    for reply in replied:
        try:
            await reply.delete()
        except:
            ...
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>
    return


@Client.on_message(filters.command('set welcome'))
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
    logger.debug(f'[{message.chat.id} ({message.message_id})] Changing welcome_message.')
    # </editor-fold>
    logger.info(message.command[0])
    await chat_data.update('welcome_message', ' '.join(message.command[1:]))
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Changed welcome_message; reporting.')
    # </editor-fold>
    await message.reply('Вітанка паспяхова зменена!')
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>
