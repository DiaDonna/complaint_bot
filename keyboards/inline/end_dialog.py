from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji


end_dialog_kb = InlineKeyboardMarkup()

end_btn = InlineKeyboardButton(text=f'{emoji.emojize(":cross_mark::telephone_receiver:")}Завершить диалог',
                               callback_data='Завершить')

end_dialog_kb.add(end_btn)
