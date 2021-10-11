from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.private & filters.incoming)
def message_handler(_: Client, message: Message):
    message.delete()
