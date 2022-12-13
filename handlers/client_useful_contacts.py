from loader import bot
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from keyboards.reply.main_menu import main_menu_kb


async def useful_contacts_from_main_menu(message: Message):

    try:
        await bot.send_message(message.chat.id,
                               f'<u>Управляющая компания:</u>\n'
                               f'<b>Диспетчерская служба ООО "УЭР-ЮГ"</b>\n'
                               f'+7 4722 35-50-06\n'
                               f'<b>Инженеры ООО "УЭР-ЮГ"</b>\n'
                               f'+7 920 566-28-86\n'
                               f'<b>Бухгалтерия ООО "УЭР-ЮГ"</b>\n'
                               f'+7 4722 35-50-06\n'
                               f'<i>Белгород, Свято-Троицкий б-р, д. 15, подъезд № 1</i>\n\n'
                               f'<u>Телефоны для открытия ворот и шлагбаума:</u>\n'
                               f'<b>Шлагбаум "Набержная"</b>\n'
                               f'+7 920 554-87-74\n'
                               f'<b>Ворота "Харьковские"</b>\n'
                               f'+7 920 554-87-40\n'
                               f'<b>Ворота "Мост"</b>\n'
                               f' +7 920 554-64-06\n'
                               f'<b>Калитка 1 "Мост"</b>\n'
                               f' +7 920 554-42-10\n'
                               f'<b>Калитка 2 "Мост"</b>\n'
                               f'+7 920 554-89-04\n'
                               f'<b>Калитка 3 "Харьковская"</b>\n'
                               f'+7 920 554-87-39\n'
                               f'<b>Калитка 4 "Харьковская"</b>\n'
                               f'+7 920 554-89-02\n\n'
                               f'<b>Охрана</b>\n'
                               f'+7 915 579-14-57\n\n'
                               f'<b>Участковый</b>\n'
                               f'Куленцова Марина Владимировна\n'
                               f'+7 999 421-53-72',
                               parse_mode='HTML',
                               allow_sending_without_reply=True,
                               reply_markup=main_menu_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


def register_handlers_client_useful_contacts(dp: Dispatcher):
    dp.register_message_handler(useful_contacts_from_main_menu, Text(endswith='Полезные контакты'), state=None)
