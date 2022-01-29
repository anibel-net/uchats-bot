import asyncio
import os
import random
import re
from typing import List

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db.ChatData import ChatData
from functions import admin_filter

CORRECT_ANSWERS: List[str] = os.environ.get('CAPTCHA_CORRECT_ANSWERS').split(';')
WRONG_ANSWERS: List[str] = os.environ.get('CAPTCHA_WRONG_ANSWERS').split(';')


@Client.on_message(filters.new_chat_members, group=101)
async def on_new_chat_member(client: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        if user.id in chat_data.verified_users:
            continue
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        wrong_answers: List[str] = []
        wrong_answers_count = random.randint(1, 3)
        while len(wrong_answers) < wrong_answers_count:
            wrong_answer = random.choice(WRONG_ANSWERS)
            if wrong_answer not in wrong_answers:
                wrong_answers.append(wrong_answer)

        buttons: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton(random.choice(CORRECT_ANSWERS), f'CR__{user.id}__{message.chat.id}')],
            *[[InlineKeyboardButton(answer, f'WR__{user.id}__{message.chat.id}')] for answer in wrong_answers]
        ]
        random.shuffle(buttons)
        await message.reply('Вітаю, перад тым, як пачаць пісаць, распавядзіце крыху пра сябе.',
                            reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(group=1)
async def on_callback_query(client: Client, query: CallbackQuery):
    correct_math = re.match(r'CR__(?P<uid>\d+)__(?P<cid>-?\d+)', query.data)
    wrong_math = re.match(r'WR__(?P<uid>\d+)__(?P<cid>-?\d+)', query.data)

    if correct_math:
        if int(correct_math.group('uid')) != query.from_user.id:
            return query.answer('Кнопка не для вас.')
        await client.restrict_chat_member(
            int(correct_math.group('cid')),
            int(correct_math.group('uid')),
            (await client.get_chat(int(correct_math.group('cid')))).permissions
        )
        chat_data = ChatData()
        await chat_data.init(query.message.chat.id)
        await chat_data.update('verified_users', [*chat_data.verified_users, int(correct_math.group('uid'))])
        welcome = await client.send_message(int(correct_math.group('cid')), chat_data.welcome_message.format(
            **(await client.get_users(int(correct_math.group('uid')))).__dict__))
        await query.message.delete()
        await asyncio.sleep(chat_data.welcome_message_timeout)
        await welcome.delete()

    if wrong_math:
        if int(wrong_math.group('uid')) != query.from_user.id:
            return query.answer('Кнопка не для вас.')
        await query.message.delete()

    await query.answer()
    return


@Client.on_message(filters.command('set welcome') & admin_filter, group=201)
async def on_set_welcome(_: Client, message: Message):
    chat_data = ChatData()
    await chat_data.init(message.chat.id)
    await chat_data.update('welcome_message', message.text.markdown[13:])
    await message.reply('Вітанка паспяхова зменена!')
