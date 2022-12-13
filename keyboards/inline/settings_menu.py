from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji


settings_menu_kb = InlineKeyboardMarkup()

change_name_btn = InlineKeyboardButton(text=f'{emoji.emojize(":hammer_and_wrench:")}Поменять имя',
                                       callback_data='Имя')
change_phone_btn = InlineKeyboardButton(text=f'{emoji.emojize(":hammer_and_wrench:")}Сменить номер',
                                        callback_data='Номер')
back_btn = InlineKeyboardButton(text=f'{emoji.emojize(":BACK_arrow:")}Назад',
                                callback_data='Назад_настройки')

settings_menu_kb.row(change_name_btn, change_phone_btn).add(back_btn)
