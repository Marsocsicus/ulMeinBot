from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from auth import tg_bot_token

bot = Bot(tg_bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
