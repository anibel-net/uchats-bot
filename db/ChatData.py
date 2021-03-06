from typing import TypedDict, Union

import motor.motor_asyncio
from bson import ObjectId

from db import db

collection: motor.motor_asyncio.AsyncIOMotorCollection = db['chats']


class _Chat(TypedDict):
    _id: ObjectId
    chat_id: int
    welcome_message: str
    welcome_message_timeout: int
    rules: str
    banned_channels: list[int]
    banned_stickers: list[str]
    banned_stickerpacks: list[str]
    verified_users: list[int]
    whitelisted_channels: list[int]


class ChatData:
    __id: ObjectId
    __chat_id: int
    welcome_message: str
    welcome_message_timeout: int
    rules: str
    banned_channels: list[int]
    banned_stickers: list[str]
    banned_stickerpacks: list[str]
    verified_users: list[int]
    whitelisted_channels: list[int]

    def __init__(self):
        ...

    async def init(self, chat_id: int):
        result: Union[_Chat, None] = await collection.find_one({'chat_id': chat_id})
        if result is None:
            insert_result = await collection.insert_one({
                'chat_id': chat_id,
                'welcome_message': 'Вітаю!',
                'rules': 'Няхай жыве анархія!',
                'welcome_message_timeout': 60,
                'banned_channels': [],
                'banned_stickers': [],
                'banned_stickerpacks': [],
                'verified_users': [],
                'whitelisted_channels': []
            })
            result: _Chat = await collection.find_one({'_id': insert_result.inserted_id})
        self.__id = result['_id'] if '_id' in result else ObjectId()
        self.__chat_id = result['chat_id'] if 'chat_id' in result else int()
        self.welcome_message = result['welcome_message'] if 'welcome_message' in result else str()
        self.welcome_message_timeout = result['welcome_message_timeout'] if 'welcome_message_timeout' in result else 60
        self.rules = result['rules'] if 'rules' in result else str()
        self.banned_channels = result['banned_channels'] if 'banned_channels' in result else list()
        self.banned_stickers = result['banned_stickers'] if 'banned_stickers' in result else list()
        self.banned_stickerpacks = result['banned_stickerpacks'] if 'banned_stickerpacks' in result else list()
        self.verified_users = result['verified_users'] if 'verified_users' in result else list()
        self.whitelisted_channels = result['whitelisted_channels'] if 'whitelisted_channels' in result else list()

    async def update(self, key, value):
        await collection.find_one_and_update({'_id': self.__id}, {"$set": {key: value}})
        result: _Chat = await collection.find_one({'_id': self.__id})
        self.__id = result['_id']
        self.__chat_id = result['chat_id']
        self.welcome_message = result['welcome_message']
        self.welcome_message_timeout = result['welcome_message_timeout']
        self.rules = result['rules']
        self.banned_channels = result['banned_channels']
        self.banned_stickers = result['banned_stickers']
        self.banned_stickerpacks = result['banned_stickerpacks']
        self.verified_users = result['verified_users']
        self.whitelisted_channels = result['whitelisted_channels']
