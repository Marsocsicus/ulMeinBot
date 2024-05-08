from distutils.util import execute
from os import curdir
import sqlite3 as sq
from create_bot import bot
import datetime

time_now = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')

def sql_start():
    global base, cur
    base = sq.connect('ul_mein.db')
    cur = base.cursor()
    if base:
        print('Database connection OK')
    base.execute('CREATE TABLE IF NOT EXISTS user_settings(user_id TEXT PRIMARY KEY, weather_city TEXT)')
    base.commit()

async def sql_add_command(state):
    try:
        async with state.proxy() as data:
            cur.execute('INSERT INTO user_settings VALUES (?, ?)', tuple(data.values()))
            base.commit()
            print(f'[{time_now}] Город пользователя {tuple(data.values())[0]} добавлен')
    except:
        async with state.proxy() as data:
            cur.execute(f'UPDATE user_settings SET user_id={tuple(data.values())[0]}, weather_city="{tuple(data.values())[1]}"')
            base.commit()
            print(f'[{time_now}] Город пользователя {tuple(data.values())[0]} обновлён')
    # async with state.proxy() as data:

    # UPDATE user_settings SET user_id = 123456, weather_city = 'asdqw'

async def sql_get_user_city(user_id):
    user_city = cur.execute(f'SELECT weather_city FROM user_settings WHERE user_id={user_id}').fetchall()[0][0]
    return user_city
    # for ret in cur.execute(f'SELECT weather_city FROM user_settings WHERE {user_id}').fetchall():
    #     await bot.send_message(message.from_user.id, ret[0])
