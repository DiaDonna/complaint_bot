from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji


application_category_kb = InlineKeyboardMarkup()

application_btn = InlineKeyboardButton(text=f'{emoji.emojize(":name_badge:")}Оставить заявку',
                                       callback_data='Заявка')
offer_btn = InlineKeyboardButton(text=f'{emoji.emojize(":light_bulb:")}Поделиться предложением',
                                 callback_data='Предложение')
back_btn = InlineKeyboardButton(text=f'{emoji.emojize(":BACK_arrow:")}Назад',
                                callback_data='Назад')

application_category_kb.row(application_btn, offer_btn).add(back_btn)
