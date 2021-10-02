from typing import TypedDict, Union

import motor.motor_asyncio
from bson import ObjectId
from loguru import logger

from db import db

collection: motor.motor_asyncio.AsyncIOMotorCollection = db['chats']


class _Chat(TypedDict):
    _id: ObjectId
    chat_id: int
    welcome_message: str
    welcome_message_timeout: int
    rules: str


class ChatData:
    __id: ObjectId
    __chat_id: int
    welcome_message: str
    welcome_message_timeout: int
    rules: str

    def __init__(self):
        ...

    async def init(self, chat_id: int):
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'Got init with chat_id {chat_id}.')
        # </editor-fold>
        result: Union[_Chat, None] = await collection.find_one({'chat_id': chat_id})
        if result is None:
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'Didn\'t found chat {chat_id}. Generating default.')
            # </editor-fold>
            insert_result = await collection.insert_one({
                'chat_id': chat_id,
                'welcome_message': 'Вітаю!',
                'rules': 'Няхай жыве анархія!',
                'welcome_message_timeout': 60,
            })
            # <editor-fold defaultstate="collapsed" desc="logging">
            logger.debug(f'Inserted default placeholder for {chat_id}.')
            # </editor-fold>
            result: _Chat = await collection.find_one({'_id': insert_result.inserted_id})
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'Chat config for {chat_id}:\n'
                     f' - _id is {result["_id"]}\n'
                     f' - chat_id is {result["chat_id"]}\n'
                     f' - welcome_message is {result["welcome_message"]}\n'
                     f' - welcome_message_timeout is {result["welcome_message_timeout"]}\n'
                     f' - rules is {result["rules"]}')
        # </editor-fold>
        self.__id = result['_id']
        self.__chat_id = result['chat_id']
        self.welcome_message = result['welcome_message']
        self.welcome_message_timeout = result['welcome_message_timeout']
        self.rules = result['rules']
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'Set all values for {chat_id}. Done.')
        # </editor-fold>

    async def update(self, key, value):
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'Got update for chat {self.__chat_id} (id is {self.__id}): "{key}"="{value}".')
        # </editor-fold>
        await collection.find_one_and_update({'_id': self.__id}, {"$set": {key: value}})
        result: _Chat = await collection.find_one({'_id': self.__id})
        # <editor-fold defaultstate="collapsed" desc="logging">
        logger.debug(f'Updated; new values for {self.__chat_id} (id is {self.__id}):\n'
                     f' - chat_id is {result["chat_id"]}\n'
                     f' - welcome_message is {result["welcome_message"]}\n'
                     f' - welcome_message_timeout is {result["welcome_message_timeout"]}\n'
                     f' - rules is {result["rules"]}\n'
                     f'Setting it as object attributes.')
        # </editor-fold>
        self.__id = result['_id']
        self.__chat_id = result['chat_id']
        self.welcome_message = result['welcome_message']
        self.welcome_message_timeout = result['welcome_message_timeout']
        self.rules = result['rules']