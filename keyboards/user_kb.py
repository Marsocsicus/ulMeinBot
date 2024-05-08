from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

btn1 = KeyboardButton(text='/ИзменитьГород')
btn2 = KeyboardButton(text='/Погода')
btn3 = KeyboardButton(text='/Курс')
btn4 = KeyboardButton(text='Отправить местоположение', request_location=True)
btn5 = KeyboardButton(text='/ПогодаЗавтра')

kb_user = ReplyKeyboardMarkup(resize_keyboard=True)
kb_debug = ReplyKeyboardMarkup(resize_keyboard=True)

kb_user.add(btn1).add(btn2).add(btn3).add(btn5)
kb_debug.add(btn4)