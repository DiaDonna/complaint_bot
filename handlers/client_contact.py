from loader import bot
from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from config_data.config import ADMIN_GROUP_ID
from database.db_loader import cur, conn

import handlers.client_settings
from keyboards.reply.main_menu import main_menu_kb
from keyboards.inline.contact_menu import contact_menu_kb
from keyboards.inline.yes_or_change_phone import yes_or_change_phone_kb
from keyboards.inline.end_dialog import end_dialog_kb
from keyboards.inline.admin_answer_or_ignore import answer_or_ignore_kb

import emoji
import re


class FSMContact(StatesGroup):
    contact_menu = State()
    recall = State()
    confirm_phone = State()
    by_chat = State()
    chatting = State()
    end_dialog = State()


async def contact_from_main_menu(message: Message):

    try:
        await FSMContact.contact_menu.set()
        await bot.send_message(message.chat.id,
                               f'{emoji.emojize(":backhand_index_pointing_down:")}_Выберите способ связи из '
                               f'нижеперечисленного списка:_',
                               parse_mode='Markdown',
                               reply_markup=contact_menu_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_contact_choice(callback: CallbackQuery, state: FSMContext):

    try:
        if callback.data == 'Перезвонить':
            await callback.message.delete()
            await FSMContact.recall.set()

            # Выполняем запрос к БД на получение номера телефона по user_id
            cur.execute('SELECT `phone_number` FROM `users` WHERE `user_id`=?', (callback.from_user.id,))
            user_phone = cur.fetchone()
            conn.commit()

            await bot.send_message(callback.message.chat.id,
                                   f'*Это Ваш верный номер телефона {user_phone[0]}?* _Если да, нажмите соответствующую '
                                   f'кнопку,_ *если нет*, впишите свой актуальный номер телефона здесь',
                                   parse_mode='Markdown',
                                   reply_markup=yes_or_change_phone_kb)

        elif callback.data == 'Чат-Бот':
            await callback.message.delete()
            await FSMContact.by_chat.set()
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":check_mark_button::telephone_receiver::check_mark_button:")}Добрый '
                                   f'день! Я - диспетчер управляющей компании "УЭР-ЮГ", готов помочь Вам. Напишите, '
                                   f'пожалуйста, интересующий Вас вопрос и ожидайте.',
                                   reply_markup=end_dialog_kb)

        elif callback.data == 'Назад_контакт':
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
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_right_phone(message: Message, state: FSMContext):

    try:
        if re.search(r'^((\+7)+(\d){10})$', message.text):
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":check_mark_button:")}*Отлично!* Наш диспетчер перезвонит Вам в '
                                   f'ближайшее время!',
                                   parse_mode='Markdown')

            # Формируем сообщение в админ-группу
            text_for_group = f'{emoji.emojize(":pushpin:")}<b>Заявка на звонок от @{message.from_user.username}</b>\n' \
                             f'<b>Указанный номер телефона:</b> {message.text}'
            await bot.send_message(chat_id=ADMIN_GROUP_ID,
                                   text=text_for_group,
                                   parse_mode='HTML')
            await state.finish()

        else:
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":no_entry: :name_badge: :no_entry:")}*Номер телефона* должен содержать'
                                   f' 11 цифр и должен обязательно содержать в начале *+7. Учтите формат и попробуйте '
                                   f'снова:*',
                                   parse_mode='Markdown')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_callback_confirmation(callback: CallbackQuery, state: FSMContext):

    try:
        if callback.data == 'Перезвонить':
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":check_mark_button:")}*Отлично!* Наш диспетчер перезвонит Вам в '
                                   f'ближайшее время!',
                                   parse_mode='Markdown')

            # Выполняем запрос к БД на получение номера телефона по user_id
            cur.execute('SELECT `phone_number` FROM `users` WHERE `user_id`=?', (callback.from_user.id,))
            user_phone = cur.fetchone()
            conn.commit()

            # Формируем сообщение в админ-группу
            text_for_group = f'{emoji.emojize(":pushpin:")}<b>Заявка на звонок от @{callback.from_user.username}</b>\n' \
                             f'<b>Номер телефона из БД:</b> {user_phone[0]}'

            await bot.send_message(chat_id=ADMIN_GROUP_ID,
                                   text=text_for_group,
                                   parse_mode='HTML')

            await state.finish()

        elif callback.data == 'Назад_изменить_номер':
            await handlers.client_settings.get_change_choice(callback=callback, state=FSMContact.recall.state,
                                                             from_back=True)

    except:
        await callback.message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_questions_by_chat(message: Message):

    try:
        # Формируем текст сообщения от пользователя в админ-группу
        # Сообщения отправляются до тех пор, пока пользователь не закончит диалог
        message_to_admin = f'{emoji.emojize(":envelope_with_arrow:")}<b>Новое сообщение от</b> ' \
                           f'@{message.from_user.username}\n\n' \
                           f'{message.text}'

        await bot.send_message(chat_id=ADMIN_GROUP_ID,
                               text=message_to_admin,
                               parse_mode='HTML',
                               reply_markup=answer_or_ignore_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def end_dialog_callback(callback: CallbackQuery, state: FSMContext):

    try:
        if callback.data == 'Завершить':
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":cross_mark::telephone_receiver:")}*Диалог с администратором '
                                   f'завершён...*',
                                   parse_mode='Markdown')
            await bot.send_message(chat_id=ADMIN_GROUP_ID, text='Диалог был завершен со стороны пользователя!')
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


def register_handlers_client_contact(dp: Dispatcher):
    dp.register_message_handler(contact_from_main_menu,
                                Text(endswith='Связаться'),
                                state=None)
    dp.register_message_handler(cancel_by_command_menu,
                                commands=['menu'],
                                state='*')
    dp.register_callback_query_handler(get_contact_choice,
                                       state=FSMContact.contact_menu)
    dp.register_message_handler(get_right_phone,
                                state=FSMContact.recall)
    dp.register_callback_query_handler(get_callback_confirmation,
                                       state=FSMContact.recall)
    dp.register_message_handler(get_questions_by_chat,
                                state=FSMContact.by_chat)
    dp.register_callback_query_handler(end_dialog_callback,
                                       state=FSMContact.by_chat)
