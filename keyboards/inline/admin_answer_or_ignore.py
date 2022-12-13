from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


answer_or_ignore_kb = InlineKeyboardMarkup()

answer_btn = InlineKeyboardButton(text='Ответить', callback_data='Ответить')
ignore_btn = InlineKeyboardButton(text='Игнорировать', callback_data='Игнорировать')

answer_or_ignore_kb.add(answer_btn, ignore_btn)
