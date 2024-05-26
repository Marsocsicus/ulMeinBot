from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import datetime
from auth import open_weather_token, open_exchange_token
from create_bot import dp, bot
from data_base import sqlite_db
from keyboards import kb_user
from keyboards import kb_debug

import datetime
import logging

time_now = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')

class FSMCity(StatesGroup):
    city = State()

# @dp.message_handler(commands=['start'])
async def start_command(message: types.Message):

    # kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add(btn2).add(btn3).add(btn)
    await message.answer('Здравствуй, перед тобой кнопки с тем, что я умею.', reply_markup=kb_user)
    # await message.answer('Здравствуй, я могу присылать тебе ежедневную сводку о погоде и курсе валют.'
    #                      '\nНо для начала небольная настройка.', reply_markup=kb)

# @dp.message_handler(commands=['Город'], state=None)
async def get_user_city(message: types.Message):
    await FSMCity.city.set()
    await message.reply('Напиши город для отслеживания', reply_markup=types.ReplyKeyboardRemove())

# @dp.message_handler(content_types=['text'], state=FSMCity.city)
async def edit_user_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['city'] = message.text
    
    await sqlite_db.sql_add_command(state)
    await message.reply('Город сохранён', reply_markup=kb_user)
    await state.finish()

# @dp.message_handler(commands=['weather'])
async def get_current_weather(message: types.Message):
    try:
        user_city = await sqlite_db.sql_get_user_city(message.from_user.id)
    except IndexError as ex:
        print(f'{time_now} [error] {ex}')
        await message.reply('Сперва выберите город :)')

    code_to_smile = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32B',
    }
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={user_city},RU&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        # print(data)

        cod = data['cod']

        if cod == 200:
            city = data['name']
            temperature = data['main']['temp']

            weather_description = data['weather'][0]['main']
            if weather_description in code_to_smile:
                wd = code_to_smile[weather_description]
            else:
                wd = 'Не разберу что-то, глянь в окно.'

            feels_like = data['main']['feels_like']
            weather = data['weather'][0]['description']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind = data['wind']['speed']
            sunrise_timestamp = datetime.datetime.fromtimestamp(
                data['sys']['sunrise'])
            sunset_timestamp = datetime.datetime.fromtimestamp(
                data['sys']['sunset'])

            await message.answer(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                f'\U0001F30D Погода в городе: {city}\n\U0001F321 Температура: {temperature}°C {wd}\n'
                                # перевод hPa в мм.рт.ст
                                f'\U0001F4A7 Влажность: {humidity}%\n\U0001F9EA Давление: {round(pressure/1.333, 1)} мм.рт.ст\n\U0001F32C Ветер: {wind} м/с\n\n'
                                # вывод только времени
                                f'\U0001F305 Восход: {datetime.datetime.time(sunrise_timestamp)}\n'
                                f'\U0001F307 Закат: {datetime.datetime.time(sunset_timestamp)}')
        else:
            print('Some trouble on server code error - ', cod)
            # await bot.send_message(453065726, 'Серверная ошибка. Проверьте название города. Текущий город ', user_city)
            await message.answer(f'Серверная ошибка. Проверьте название города.\nТекущий город: {user_city}')
            
    except Exception as ex:
        print(f'[error] Unexpecting error <{ex}>')
        await message.answer(f'Проверьте название города.\nТекущий город: {user_city}')

async def get_tomorrow_weather(message: types.Message):
    try:
        user_city = await sqlite_db.sql_get_user_city(message.from_user.id)
    except IndexError as ex:
        print(f'{time_now} [error] {ex}')
        await message.reply('Сперва выберите город :)')

    output = 0

    code_to_smile = {
    'Clear': 'Ясно \U00002600',
    'Clouds': 'Облачно \U00002601',
    'Rain': 'Дождь \U00002614',
    'Drizzle': 'Дождь \U00002614',
    'Thunderstorm': 'Гроза \U000026A1',
    'Snow': 'Снег \U0001F328',
    'Mist': 'Туман \U0001F32B',
    }
    
    '''
    %t Temperature
    %h humidity
    %P pressure
    %w wind
    %S sunrise
    %s sunset

    https://wttr.in/Voronezh:2?format=j2
    '''
    try:
        format = '%t+%h+%P+%w+%S+%s'
        weather_request = requests.get(
            f'http://wttr.in/{user_city}?format={format}').text.split()


        await message.answer(f'***Погода на завтра***\n'
                            f'\U0001F30D Погода в городе: {user_city}\n\U0001F321 Температура: {weather_request(user_city, "%t")}')
    except Exception as ex:
        print(f'[error] Unexpecting error <{ex}>')

async def get_currency(message: types.Message):
    try:
        response = requests.get(url='https://yobit.net/api/3/ticker/btc_usd')
        data_btc = response.json()
        btc_price = f"BTC: {round(data_btc.get('btc_usd').get('last'), 2)}$"

        response_usd = requests.get(
            url = f'https://openexchangerates.org/api/latest.json?app_id={open_exchange_token}&base=USD&symbols=RUB').json()
        data_usdrub = response_usd['rates']['RUB']
        usdrub_price = f"USD: {round(data_usdrub, 2)}₽"

        await message.answer(f'Текущий курс валют:\n\U0001FA99{btc_price}\n\U0001F4B5{usdrub_price}')
    except Exception as ex:
        print(ex)
        await message.answer('Что-то пошло не так :(')

async def handle_location(message: types.Message):
    current_position = (message.location.longitude, message.location.latitude)
    print(current_position)

async def cmd_locate_me(message: types.Message):
    reply = "Click on the button below to share your location"
    await message.answer(reply, reply_markup=kb_debug)

def register_handlers_user(dp : Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(get_user_city, commands=['ИзменитьГород'], state=None)
    dp.register_message_handler(edit_user_city, content_types=['text'], state=FSMCity.city)
    dp.register_message_handler(get_current_weather, commands=['Погода'])
    dp.register_message_handler(get_tomorrow_weather, commands=['ПогодаЗавтра'])
    dp.register_message_handler(get_currency, commands=['Курс'])
    dp.register_message_handler(handle_location, content_types=['location'])
    dp.register_message_handler(cmd_locate_me, commands=['debug'])
