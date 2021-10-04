from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import Message


@Client.on_message(filters.command('report', ['/', '!']) | filters.command(['admin', 'admins'], '@'), group=25)
async def report_handler(client: Client, message: Message):
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
    admins = client.iter_chat_members(message.chat.id, filter='administrators')
    if admins is None:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.warning(f'[{message.chat.id} ({message.message_id})] Couldn\'t find any admin. Reporting.')
        # </editor-fold>
        await message.reply('Нешта пайшло не так. Калі ласка, паспрабуйце яшчэ раз ці пазней.')
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.warning(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return
    async for admin in admins:
        if admin.user.is_self or admin.user.is_bot:
            continue
        try:
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] '
                         f'Trying to report to {admin.user.id} ({admin.user.username})...')
            # </editor-fold>
            await client.send_message(admin.user.id,
                                      f'Новая скарга з чата: '
                                      f'https://t.me/c/{message.chat.id * -1 - 1000000000000}/{message.message_id}')
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] '
                         f'Reported to {admin.user.id} ({admin.user.username}).')
            # </editor-fold>
        except BadRequest as e:
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.error(f'[{message.chat.id} ({message.message_id})] '
                         f'Tried to report to {admin.user.id} ({admin.user.username}), but got {e}')
            # </editor-fold>
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Replied report.')
    # </editor-fold>
    await message.reply('Перадана адміністратарам-людзям.')
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>
    return
