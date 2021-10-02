import os

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGODB_CONNECTION_STRING') or 'mongodb://localhost')
db: motor.motor_asyncio.AsyncIOMotorDatabase = client['uchats-bot']
