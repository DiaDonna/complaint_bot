from loader import bot
from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from database.db_loader import cur, conn

from keyboards.reply.main_menu import main_menu_kb
from keyboards.inline.settings_menu import settings_menu_kb

import emoji
import re


class FSMSettings(StatesGroup):
    settings_menu = State()
    change_name = State()
    change_phone_number = State()


async def settings_from_main_menu(message: Message):

    try:
        await FSMSettings.settings_menu.set()
        await bot.send_message(message.chat.id,
                               f'{emoji.emojize(":gear:")}Тут вы сможете поменять *Имя* и *Фамилию* в Базе данных нашего '
                               f'бота или же можете поменять Ваш *номер телефона*, если Вы изначально вводили что-то '
                               f'неверно. Выберите, что хотите поменять или вернитесь назад в *главное меню*:',
                               parse_mode='Markdown',
                               reply_markup=settings_menu_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_change_choice(callback: CallbackQuery, state: FSMContext, from_back: bool = False):

    try:
        if from_back:
            await callback.message.delete()
            await FSMSettings.change_phone_number.set()
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":hammer_and_wrench:")}_Отправьте свой номер телефона, чтобы поменять '
                                   f'настройки:_',
                                   parse_mode='Markdown')

        if callback.data == 'Имя':
            await callback.message.delete()
            await FSMSettings.change_name.set()
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":hammer_and_wrench:")}_Отправьте своё Имя и Фамилию, чтобы поменять '
                                   f'настройки:_',
                                   parse_mode='Markdown')

        elif callback.data == 'Номер':
            await callback.message.delete()
            await state.finish()
            await FSMSettings.change_phone_number.set()
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":hammer_and_wrench:")}_Отправьте свой номер телефона, чтобы поменять '
                                   f'настройки:_',
                                   parse_mode='Markdown')

        elif callback.data == 'Назад_настройки':
            await callback.message.delete()
            await state.finish()
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":airplane:")}*Добро пожаловать* в _главное меню чат-бота Управляющей '
                                   f'компании "УЭР-ЮГ"._ Здесь вы можете оставить заявку для управляющей компании или '
                                   f'направить своё предложение по управлению домом. Просто воспользуйтесь кнопками *меню*,'
                                   f' чтобы взаимодействовать с функциями бота.',
                                   parse_mode='Markdown',
                                   reply_markup=main_menu_kb)

    except:
        await callback.message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_change_name(message: Message, state: FSMContext):

    try:
        if len(message.text.split(' ')) == 2 \
                and all(word.isalpha() for word in message.text.split(' ')) \
                and message.text.istitle() \
                and re.search(r'[А-Яа-я]', message.text):
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":hammer_and_wrench::check_mark_button::hammer_and_wrench:")}Настройки '
                                   f'*имени* успешно применены!',
                                   parse_mode='Markdown')

            # Обновляем данные (Имя и Фамилию) в БД по user_id
            cur.execute('UPDATE `users` SET `user_info`=? WHERE `user_id`=?', (message.text, message.from_user.id))
            conn.commit()

            await state.finish()

        else:
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":no_entry: :name_badge:")}*Имя* и *Фамилия* должны быть введены через '
                                   f'один _пробел_, и должны быть написаны через _кириллицу_. Также должны быть _заглавные '
                                   f'буквы_. *Учтите формат и попробуйте снова:*',
                                   parse_mode='Markdown')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_change_phone_number(message: Message, state: FSMContext):

    try:
        if re.search(r'^((\+7)+(\d){10})$', message.text):
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":hammer_and_wrench::check_mark_button::hammer_and_wrench:")}Настройки '
                                   f'*номера* успешно применены!',
                                   parse_mode='Markdown')

            # Обновляем данные (Номер телефона) в БД по user_id
            cur.execute('UPDATE `users` SET `phone_number`=? WHERE `user_id`=?', (message.text, message.from_user.id))
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


async def cancel_by_command_menu(message: Message, state: FSMContext):

    try:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()

        cur.execute('SELECT * FROM `users` WHERE `user_id`=?', (message.from_user.id,))
        user_info = cur.fetchone()
        conn.commit()

        if user_info[6] == 1:
            await bot.send_message(message.chat.id, 'Вы были забанены администратором. Функции бота для вас недоступны.',
                                   reply_markup=ReplyKeyboardRemove())

        else:
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":airplane:")}*Добро пожаловать* в _главное меню чат-бота Управляющей '
                                   f'компании "УЭР-ЮГ"._ Здесь вы можете оставить заявку для управляющей компании или '
                                   f'направить своё предложение по управлению домом. Просто воспользуйтесь кнопками *меню*,'
                                   f' чтобы взаимодействовать с функциями бота.',
                                   parse_mode='Markdown',
                                   reply_markup=main_menu_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


def register_handlers_client_settings(dp: Dispatcher):
    dp.register_message_handler(settings_from_main_menu,
                                Text(endswith='Настройки'),
                                state=None)
    dp.register_message_handler(cancel_by_command_menu,
                                commands=['menu'],
                                state='*')
    dp.register_callback_query_handler(get_change_choice,
                                       state=FSMSettings.settings_menu)
    dp.register_message_handler(get_change_name,
                                state=FSMSettings.change_name)
    dp.register_message_handler(get_change_phone_number,
                                state=FSMSettings.change_phone_number)
