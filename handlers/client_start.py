from loader import bot
from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from database.db_loader import cur, conn

from keyboards.reply.main_menu import main_menu_kb

import emoji
import re


class FSMStartInfo(StatesGroup):
    name = State()
    phone_number = State()


async def client_start(message: Message, state: FSMContext):

    await FSMStartInfo.name.set()

    cur.execute('SELECT * FROM `users` WHERE `user_id`=?', (message.from_user.id,))
    user_info = cur.fetchone()
    conn.commit()
    if user_info:
        if user_info[6] == 1:
            await state.finish()
            await bot.send_message(message.chat.id, 'Вы были заблокированы администратором.\n'
                                                    'Функции бота для вас недоступны.',
                                   reply_markup=ReplyKeyboardRemove())

        else:
            await state.finish()
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":red_exclamation_mark:")}<i>Ваши данные уже есть в базе данных:</i>\n'
                                   f'<b>Имя Фамилия:</b> {user_info[4]}\n'
                                   f'<b>Номер телефона:</b> {user_info[5]}\n\n'
                                   f'Если Вы хотите изменить свои данные, то воспользуйтесь кнопкой "Настройки" '
                                   f'в Главном Меню или воспользуйтесь нужной Вам командой.',
                                   parse_mode='HTML',
                                   reply_markup=main_menu_kb)

    else:
        await bot.send_message(message.chat.id,
                               f'{emoji.emojize(":sun:")}Доброго времени суток, бот создан, чтобы обрабатывать заявки и'
                               f' обращения пользователей. Чтобы воспользоваться этим, пришлите для начала Ваше '
                               f'*Имя* и *Фамилию*',
                               parse_mode='Markdown')


async def get_name(message: Message, state: FSMContext):

    try:
        if len(message.text.split(' ')) == 2 \
                and all(word.isalpha() for word in message.text.split(' ')) \
                and message.text.istitle()\
                and re.search(r'[А-Яа-я]', message.text):

            await FSMStartInfo.phone_number.set()
            print(message)
            async with state.proxy() as data:
                data['user_id'] = message.from_user.id
                data['chat_id'] = message.chat.id
                data['user_name'] = message.from_user.username
                data['user_info'] = message.text
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":telephone_receiver:")}Теперь отправьте ваш *номер телефона* '
                                   f'через *+7* следующим сообщением:',
                                   parse_mode='Markdown')

        else:
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":no_entry: :name_badge:")}*Имя* и *Фамилия* должны быть введены через '
                                   f'один _пробел_, и должны быть написаны через _кириллицу_. Также должны быть _заглавные '
                                   f'буквы_. *Учтите формат и попробуйте снова:*',
                                   parse_mode='Markdown')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_phone_number(message: Message, state: FSMContext):

    try:
        if re.search(r'^((\+7)+(\d){10})$', message.text):
            async with state.proxy() as data:
                data['phone_number'] = message.text
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":airplane:")}*Добро пожаловать* в _главное меню чат-бота Управляющей '
                                   f'компании "УЭР-ЮГ"._ Здесь вы можете оставить заявку для управляющей компании или '
                                   f'направить своё предложение по управлению домом. Просто воспользуйтесь кнопками *меню*,'
                                   f' чтобы взаимодействовать с функциями бота.',
                                   parse_mode='Markdown',
                                   reply_markup=main_menu_kb)

            cur.execute('INSERT INTO users (user_id, chat_id, user_name, user_info, phone_number, is_block) '
                        'VALUES (?, ?, ?, ?, ?, ?)',
                        (data['user_id'],
                         data['chat_id'],
                         data['user_name'],
                         data['user_info'],
                         data['phone_number'],
                         False))
            conn.commit()
            await state.finish()

        else:
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":no_entry: :name_badge: :no_entry:")}*Номер телефона* должен содержать'
                                   f' 11 цифр и должен обязательно содержать в начале *+7. Учтите формат и попробуйте '
                                   f'снова:*',
                                   parse_mode='Markdown')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(client_start, commands=['start'])
    dp.register_message_handler(get_name, state=FSMStartInfo.name)
    dp.register_message_handler(get_phone_number, state=FSMStartInfo.phone_number)
