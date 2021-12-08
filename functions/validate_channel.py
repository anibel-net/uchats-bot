import asyncio
from typing import TypedDict, Union

from loguru import logger
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied, UsernameInvalid, FloodWait


class ParsedChannel(TypedDict):
    id: int
    username: Union[str, None]
    title: str


async def validate_channel(client: Client, channel_cred: str) -> Union[ParsedChannel, None]:
    try:
        channel = await client.get_chat(channel_cred)
        if channel.type != 'channel':
            return
        return {
            'id': channel.id,
            'username': channel.username,
            'title': str(channel.title)
        }
    except (PeerIdInvalid, UsernameNotOccupied, UsernameInvalid) as e:
        logger.error(f"[{channel_cred}] Couldn't convert find channel.")
        return
    except FloodWait as e:
        logger.error(f'[{channel_cred}] Got FloodWait, waiting {e.x} seconds.')
        await asyncio.sleep(e.x)
        return await validate_channel(client, channel_cred)
