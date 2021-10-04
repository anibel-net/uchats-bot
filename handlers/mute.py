import asyncio
import re
import time
from typing import TypedDict

from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from functions import is_admin

PATTERN = re.compile(r'^/(mute|ro) ?(?P<term>(?P<count>\d+(\.\d+)?) ?(?P<unit>[a-z]+))? ?(?P<reason>.+)?$', re.I)


class PeriodInSeconds(TypedDict):
    minute: int
    hour: int
    day: int


PERIOD_IN_SECONDS: PeriodInSeconds = {
    'minute': 60,
    'hour': 3600,
    'day': 86400
}


@logger.catch
@Client.on_message(filters.command(['mute', 'ro']) & filters.group, group=20)
async def on_mute(client: Client, message: Message):
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
    if message.reply_to_message is None:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Message have no reply_to_message; deleting...')
        # </editor-fold>
        await message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return
    if message.reply_to_message.from_user is None:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Replied not to user; deleting...')
        # </editor-fold>
        await message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return
    target = message.reply_to_message.from_user
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.debug(f'[{message.chat.id} ({message.message_id})] Replied user (mute target) is '
                 f'@{target.username} ({target.id}).')
    # </editor-fold>
    if message.from_user:
        if not (await client.get_chat_member(message.chat.id, message.from_user.id)).can_restrict_members:
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] user @{message.from_user.username} '
                         f'({message.from_user.id}) haven\'t got can_restrict_members permission. Informing...')
            # </editor-fold>
            reply = await message.reply('У вас бракуе праваў, каб зрабіць гэта.')
            await asyncio.sleep(10)
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] User informed 10 seconds ago. '
                         f'Deleting message and reply...')
            # </editor-fold>
            await message.delete()
            await reply.delete()
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
            # </editor-fold>
            return
    if await is_admin(client, message.chat.id, message.reply_to_message.from_user.id):
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Can\'t mute because replied user is administrator; '
                     f'informing...')
        # </editor-fold>
        reply = await message.reply('Не магу абмежаваць гэтага карыстальніка, бо ён з\'яўляеца адміністратам.')
        await asyncio.sleep(10)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] User informed 10 seconds ago. '
                     f'Deleting message and reply...')
        # </editor-fold>
        await message.delete()
        await reply.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return
    match = PATTERN.match(message.text)
    reason = f'\nПрычына: <i>{match.group("reason")}</i>' if match.group('reason') else ''
    if match.group('term') is None:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] No term specified; muting for 1 day...')
        # </editor-fold>
        await client.restrict_chat_member(message.chat.id, target.id,
                                          ChatPermissions(can_send_messages=False), round(time.time()) + 86400)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Successfully muted target;'
                     f'deleting message with command and informing...')
        # </editor-fold>
        await message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Successfully Deleted message')
        # </editor-fold>
        await message.reply_to_message.reply(f'Карыстальнік <a href="tg://user?{target.id}">{target.first_name}'
                                             f'{f" {target.last_name}" if target.last_name else ""}'
                                             f'</a> быў абмежаваны на наступныя 24 гадзіны, у гэты час ён не зможа'
                                             f'пісаць паведамленні ў чат.')
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Successfully informed about mute.')
        logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return
    if match.group('count'):
        count = float(match.group('count'))
        if match.group('unit') in ('m', 'min', 'minute', 'minutes'):
            mute_time = round(count * PERIOD_IN_SECONDS['minute'])
            unit_name = 'хвілін'
        elif match.group('unit') in ('h', 'hour', 'hours'):
            mute_time = round(count * PERIOD_IN_SECONDS['hour'])
            unit_name = 'гадзін'
        elif match.group('unit') in ('d', 'day', 'days'):
            mute_time = round(count * PERIOD_IN_SECONDS['day'])
            unit_name = 'дзён'
        else:
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'[{message.chat.id} ({message.message_id})] unit of term is invalid; ignoring...')
            logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
            # </editor-fold>
            return
        await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=False),
                                          round(time.time()) + mute_time)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Successfully muted target; '
                     f'deleting message with command and informing...')
        # </editor-fold>
        await message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Successfully Deleted message')
        # </editor-fold>
        await message.reply_to_message.reply(f'Карыстальнік <a href="tg://user?{target.id}">{target.first_name}'
                                             f'{f" {target.last_name}" if target.last_name else ""}'
                                             f'</a> быў абмежаваны на наступныя {str(count)} {unit_name}, '
                                             f'у гэты час ён не зможа пісаць паведамленні ў чат.{reason}')
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'[{message.chat.id} ({message.message_id})] Successfully informed about mute.')
        logger.debug(f'[{message.chat.id} ({message.message_id})] Done.')
        # </editor-fold>
        return
