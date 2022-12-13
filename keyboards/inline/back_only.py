from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import emoji


back_only_kb = InlineKeyboardMarkup()

back_btn = InlineKeyboardButton(text=f'{emoji.emojize(":BACK_arrow:")}Назад',
                                callback_data='Назад')

back_only_kb.add(back_btn)
