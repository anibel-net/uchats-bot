import asyncio
from typing import TypedDict, Union

from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid

from db.ChatData import ChatData
from functions import is_admin


class BanCandidate(TypedDict):
    id: int
    username: Union[str, None]
    title: str


@Client.on_message(filters.forwarded, group=107)
async def on_forward(client: Client, message: Message):
    if message.from_user:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received forward'
                    f'from @{message.from_user.username} ({message.from_user.id}) from {message.forward_from_chat.id}')
        # </editor-fold>
        if await is_admin(client, message.chat.id, message.from_user.id):
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.info(f'[{message.chat.id} ({message.message_id})] user @{message.from_user.username} '
                        f'({message.from_user.id}) is administrator, ignoring.')
            # </editor-fold>
            return
    if message.sender_chat:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Received forward'
                    f'from @{message.sender_chat.username} ({message.sender_chat.id}) '
                    f'from {message.forward_from_chat.id}. Ignoring.')
        # </editor-fold>
        return
    if message.forward_from_chat.type != 'channel':
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Forwarded not from channel. Ignoring.')
        # </editor-fold>
        return
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Initialization chat_data...')
    # </editor-fold>
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] initialized.')
    logger.info(f'[{message.chat.id} ({message.message_id})] Checking channel.')
    # </editor-fold>
    if message.forward_from_chat.id in chat_data.banned_channels:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Channel {message.forward_from_chat.id} banned. '
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


@Client.on_message(filters.command('ban channel'), group=207)
async def on_ban_channel(client: Client, message: Message):
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
    logger.info(f'[{message.chat.id} ({message.message_id})] Fetching channels.')
    # </editor-fold>
    if len(message.command) == 1 and \
            (message.reply_to_message is None
             or message.reply_to_message.forward_from_chat is None
             or message.reply_to_message.forward_from_chat.type != 'channel'):
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] No channels passed. Reporting...')
        # </editor-fold>
        reply = await message.reply('Калі ласка, выкарыстоўвайце `/ban channel @username` '
                                    'ці `/ban channel id` альбо дашліце гэтае паведамленне '
                                    'ў адказ на перадасланы пост з канала, які хочаце забаніць.')
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

    ban_candidates: list[BanCandidate] = []

    if message.reply_to_message and message.reply_to_message.forward_from_chat \
            and message.reply_to_message.forward_from_chat.type == 'channel':
        ban_candidates.append({
            'id': message.reply_to_message.forward_from_chat.id,
            'username': message.reply_to_message.forward_from_chat.username,
            'title': str(message.reply_to_message.forward_from_chat.title)
        })

    if len(message.command) > 1:
        for arg in message.command[1:]:
            try:
                # <editor-fold defaultstate="collapsed" desc="logging">
                logger.info(f'[{message.chat.id} ({message.message_id})] Validating "{arg}" as channel.')
                # </editor-fold>
                channel = await client.get_chat(arg)
                if channel.type != 'channel':
                    # <editor-fold defaultstate="collapsed" desc="logging">
                    logger.info(f'[{message.chat.id} ({message.message_id})] "{arg}" is not channel. Skipping...')
                    # </editor-fold>
                    continue
                ban_candidates.append({
                    'id': channel.id,
                    'username': channel.username,
                    'title': str(channel.title)
                })
            except PeerIdInvalid as e:
                # <editor-fold defaultstate="collapsed" desc="logging">
                logger.error(f'[{message.chat.id} ({message.message_id})] Couldn\t convert find channel "{arg}"'
                             f'. Skipping...')
                # </editor-fold>
                continue

    logger.debug(ban_candidates)

    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Ban candidates: '
                f'{", ".join([str(i["id"]) for i in ban_candidates])}.')
    # </editor-fold>
    await chat_data.update('banned_channels', [*chat_data.banned_channels, *[i['id'] for i in ban_candidates]])
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Added channels to banned Reporting...')
    # </editor-fold>
    reply = await message.reply('Паспяхова забанены каналы: {channels_list}.'.format(
        channels_list=", ".join([chat["title"] for chat in ban_candidates])
    ))
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