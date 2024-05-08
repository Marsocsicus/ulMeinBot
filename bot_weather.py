from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db
from handlers import user

async def on_startup(_):
    print('Bot is running')
    sqlite_db.sql_start()

user.register_handlers_user(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)