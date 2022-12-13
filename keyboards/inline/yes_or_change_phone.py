from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji


yes_or_change_phone_kb = InlineKeyboardMarkup()

yes_btn = InlineKeyboardButton(text=f'{emoji.emojize(":check_mark_button:")}Да',
                               callback_data='Перезвонить')
change_phone_btn = InlineKeyboardButton(text=f'{emoji.emojize(":BACK_arrow:")}Оставить номер телефона',
                                        callback_data='Назад_изменить_номер')

yes_or_change_phone_kb.row(yes_btn, change_phone_btn)
