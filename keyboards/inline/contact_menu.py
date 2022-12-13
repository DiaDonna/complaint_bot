from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji


contact_menu_kb = InlineKeyboardMarkup()

recall_btn = InlineKeyboardButton(text=f'{emoji.emojize(":telephone_receiver:")}Перезвоните мне',
                                       callback_data='Перезвонить')
by_chat_btn = InlineKeyboardButton(text=f'{emoji.emojize(":telephone_receiver:")}Свяжитесь со мной в чат-боте',
                                        callback_data='Чат-Бот')
back_btn = InlineKeyboardButton(text=f'{emoji.emojize(":BACK_arrow:")}Назад',
                                callback_data='Назад_контакт')

contact_menu_kb.row(recall_btn, by_chat_btn).add(back_btn)
