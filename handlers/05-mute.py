import asyncio
import re
import time
from typing import TypedDict

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


@Client.on_message(filters.command(['mute', 'ro']) & filters.group, group=205)
async def on_mute(client: Client, message: Message):
    if message.from_user:
        if not (await client.get_chat_member(message.chat.id, message.from_user.id)).can_restrict_members:
            return
    if message.sender_chat:
        return
    if message.reply_to_message is None:
        await message.delete()
        return
    if message.reply_to_message.from_user is None:
        await message.delete()
        return
    target = message.reply_to_message.from_user
    if await is_admin(client, message.chat.id, target.id):
        reply = await message.reply('Не магу абмежаваць гэтага карыстальніка, бо ён з\'яўляеца адміністратам.')
        await asyncio.sleep(10)
        await message.delete()
        await reply.delete()
        return
    match = PATTERN.match(message.text)
    reason = f'\nПрычына: <i>{match.group("reason")}</i>' if match.group('reason') else ''
    if match.group('term') is None:
        await client.restrict_chat_member(message.chat.id, target.id,
                                          ChatPermissions(can_send_messages=False), round(time.time()) + 86400)
        await message.delete()
        await message.reply_to_message.reply(f'Карыстальнік <a href="tg://user?{target.id}">{target.first_name}'
                                             f'{f" {target.last_name}" if target.last_name else ""}'
                                             f'</a> быў абмежаваны на наступныя 24 гадзіны, у гэты час ён не зможа'
                                             f'пісаць паведамленні ў чат.')
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
            return
        await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=False),
                                          round(time.time()) + mute_time)
        await message.delete()
        await message.reply_to_message.reply(f'Карыстальнік <a href="tg://user?{target.id}">{target.first_name}'
                                             f'{f" {target.last_name}" if target.last_name else ""}'
                                             f'</a> быў абмежаваны на наступныя {str(count)} {unit_name}, '
                                             f'у гэты час ён не зможа пісаць паведамленні ў чат.{reason}')
        return
