from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import emoji


pass_or_back_kb = InlineKeyboardMarkup()

pass_btn = InlineKeyboardButton(text=f'{emoji.emojize(":right_arrow:")}Пропустить',
                                callback_data='Пропустить')
back_btn = InlineKeyboardButton(text=f'{emoji.emojize(":BACK_arrow:")}Назад',
                                callback_data='Назад')

pass_or_back_kb.add(pass_btn, back_btn)
