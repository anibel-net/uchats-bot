from pyrogram import Client


async def is_admin(client: Client, chat_id: int, user_id: int):
    return (await client.get_chat_member(chat_id, user_id)).status in ('creator', 'administrator')
