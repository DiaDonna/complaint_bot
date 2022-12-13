from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

application_btn = KeyboardButton(f'{emoji.emojize(":name_badge:")}Оставить заявку')
contact_btn = KeyboardButton(f'{emoji.emojize(":telephone_receiver:")}Связаться')
settings_btn = KeyboardButton(f'{emoji.emojize(":gear:")}Настройки')
useful_contacts_btn = KeyboardButton(f'{emoji.emojize(":telephone:")}Полезные контакты')

main_menu_kb.row(application_btn, contact_btn).add(settings_btn).add(useful_contacts_btn)

