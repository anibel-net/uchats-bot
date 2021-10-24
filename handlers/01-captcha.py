import asyncio
import random
import re
from typing import List

from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db.ChatData import ChatData
from functions import is_admin

CORRECT_ANSWERS: List[str] = [
    'Я чалавек',
    'Я не бот'
]
WRONG_ANSWERS: List[str] = [
    'Я бот',
    'Я спамер',
    'Я не буду размаўляць па-беларуску',
    'Я буду абражаць іншых',
    'Я чарговы фейк Сямёна'
]


@Client.on_message(filters.new_chat_members, group=101)
async def on_new_chat_member(client: Client, message: Message):
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] New user joined chat: '
                + ', '.join(map(lambda user: f'@{user.username} ({user.id})', message.new_chat_members)))
    # </editor-fold>
    for user in message.new_chat_members:
        if user.is_bot:
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.info(f'[{message.chat.id} ({message.message_id})] User {user.id} is bot; skipping.')
            # </editor-fold>
            continue
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Restricted user {user.id}.')
        # </editor-fold>
        wrong_answers: List[str] = []
        wrong_answers_count = random.randint(2, len(WRONG_ANSWERS) - 1)
        while len(wrong_answers) < wrong_answers_count:
            wrong_answer = random.choice(WRONG_ANSWERS)
            if wrong_answer not in wrong_answers:
                wrong_answers.append(wrong_answer)

        buttons: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton(random.choice(CORRECT_ANSWERS), f'CR__{user.id}__{message.chat.id}')],
            *[[InlineKeyboardButton(answer, f'WR__{user.id}__{message.chat.id}')] for answer in wrong_answers]
        ]
        random.shuffle(buttons)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Generated buttons for {user.id}: '
                    + ', '.join(map(lambda button: f'{button[0].text} ({button[0].callback_data[:2]})', buttons)))
        # </editor-fold>
        await message.reply('Вітаю, перад тым, як пачаць пісаць, распавядзіце крыху пра сябе.',
                            reply_markup=InlineKeyboardMarkup(buttons))
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{message.chat.id} ({message.message_id})] Sent captcha message to {user.id}.')
        # </editor-fold>


@Client.on_callback_query(group=1)
async def on_callback_query(client: Client, query: CallbackQuery):
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{query.id}] Got callback_query: {query.data}.')
    # </editor-fold>
    correct_math = re.match(r'CR__(?P<uid>\d+)__(?P<cid>-?\d+)', query.data)
    wrong_math = re.match(r'WR__(?P<uid>\d+)__(?P<cid>-?\d+)', query.data)

    if correct_math:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Answer is correct.')
        # </editor-fold>
        if int(correct_math.group('uid')) != query.from_user.id \
                and is_admin(client, int(correct_math.group('cid')), query.from_user.id):
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.info(f'[{query.id}] Done.')
            # </editor-fold>
            return query.answer('Кнопка не для вас.')
        await client.restrict_chat_member(
            int(correct_math.group('cid')),
            int(correct_math.group('uid')),
            (await client.get_chat(int(correct_math.group('cid')))).permissions
        )
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Initialization chat_data...')
        # </editor-fold>
        chat_data = ChatData()
        await chat_data.init(query.message.chat.id)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] initialized.')
        logger.info(f'[{query.id}] Sending welcome.')
        # </editor-fold>
        welcome = await client.send_message(int(correct_math.group('cid')), chat_data.welcome_message.format(
            **(await client.get_users(int(correct_math.group('uid')))).__dict__))
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Welcome sent.')
        logger.info(f'[{query.id}] Deleting captcha message.')
        # </editor-fold>
        await query.message.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Deleted captcha message.')
        logger.info(f'[{query.id}] Sleeping.')
        # </editor-fold>
        await asyncio.sleep(chat_data.welcome_message_timeout)
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Awoke.')
        logger.info(f'[{query.id}] Deleting welcome message.')
        # </editor-fold>
        await welcome.delete()
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Deleted welcome message.')
        # </editor-fold>

    if wrong_math:
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.info(f'[{query.id}] Answer is wrong.')
        # </editor-fold>
        if int(wrong_math.group('uid')) != query.from_user.id \
                and is_admin(client, int(wrong_math.group('cid')), query.from_user.id):
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.info(f'[{query.id}] Done.')
            # </editor-fold>
            return query.answer('Кнопка не для вас.')
        await query.message.delete()

    await query.answer()
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{query.id}] Done.')
    # </editor-fold>
    return


@Client.on_message(filters.command('set welcome'), group=201)
async def on_set_welcome(client: Client, message: Message):
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
    logger.info(f'[{message.chat.id} ({message.message_id})] Changing welcome_message.')
    # </editor-fold>
    await chat_data.update('welcome_message', ' '.join(message.text.markdown[13:]))
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Changed welcome_message; reporting.')
    # </editor-fold>
    await message.reply('Вітанка паспяхова зменена!')
    # <editor-fold defaultstate="collapsed" desc="logging">
    logger.info(f'[{message.chat.id} ({message.message_id})] Done.')
    # </editor-fold>