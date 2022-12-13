from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


user_info_kb = InlineKeyboardMarkup()

fio_btn = InlineKeyboardButton(text='По ФИО', callback_data='fio')
phone_btn = InlineKeyboardButton(text='По телефону', callback_data='phone')

user_info_kb.add(fio_btn, phone_btn)
