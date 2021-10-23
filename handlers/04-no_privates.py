from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.private & filters.incoming, group=704)
def on_private(_: Client, message: Message):
    message.delete()
