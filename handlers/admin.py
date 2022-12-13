from loader import bot
from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from database.db_loader import cur, conn

from keyboards.reply.main_menu import main_menu_kb
from keyboards.inline.admin_user_info import user_info_kb

import emoji


admins_ID = []


class FSMActions(StatesGroup):
    info_choice = State()
    info_param = State()
    answer = State()
    spam = State()
    block = State()
    unblock = State()


async def check_admin(message: Message):
    try:
        global admins_ID
        if message.from_user.id not in admins_ID:
            admins_ID.append(message.from_user.id)

        await message.answer(text=f'<b>Список команд для администраторов группы:</b>\n\n'
                                  f'/admin - Показать список команд для администраторов\n\n'
                                  f'/chat_id - Узнать chat_id группы\n\n'
                                  f'/info_user - Информация из БД о человеке по его номеру телефона '
                                  f'или username\n\n'
                                  f'/spam - Выполнить рассылку по БД\n\n'
                                  f'/block - Заблокировать пользователя\n\n'
                                  f'/unblock - Разблокировать пользователя\n',
                             parse_mode='HTML')
    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_chat_id(message: Message):

    try:
        global admins_ID
        if message.from_user.id not in admins_ID:
            admins_ID.append(message.from_user.id)

        await message.reply(f'Chat ID: {message.chat.id}')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def command_spam(message: Message):

    try:
        global admins_ID
        if message.from_user.id not in admins_ID:
            admins_ID.append(message.from_user.id)

        await FSMActions.spam.set()
        await message.answer(f'Напишите текст рассылки *одним сообщением* в том виде, в котором хотите донести '
                             f'до пользователя{emoji.emojize(":down_arrow:")}',
                             parse_mode='Markdown')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def making_spam(message: Message, state: FSMContext):

    try:
        cur.execute('SELECT `chat_id` from `users`')
        spam_base = cur.fetchall()
        conn.commit()

        for chat_id in spam_base:
            await bot.send_message(chat_id[0], message.text)

        await message.answer(f'Рассылка завершена!{emoji.emojize(":check_mark:")}')
        await state.finish()

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def command_info_user(message: Message):

    try:
        global admins_ID
        if message.from_user.id not in admins_ID:
            admins_ID.append(message.from_user.id)

        await FSMActions.info_choice.set()
        await message.answer(f'По какому критерию искать пользователя в базе данных?', reply_markup=user_info_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def viewing_user_info_by(callback: CallbackQuery):

    try:
        await FSMActions.info_param.set()
        await callback.message.delete()

        if callback.data == 'fio':
            await callback.message.answer(f'Введите Имя Фамилию (через 1 пробел с заглавных букв)'
                                          f' {emoji.emojize(":down_arrow:")}')

        elif callback.data == 'phone':
            await callback.message.answer(f'Введите номер телефона в формате +79995558833 {emoji.emojize(":down_arrow:")}')

    except:
        await callback.message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def viewing_user_info(message: Message, state: FSMContext):

    try:
        if message.text.startswith('+'):
            cur.execute('SELECT `user_id`, `user_name` from `users` WHERE `phone_number`=?', (message.text,))
            user_info = cur.fetchone()
            conn.commit()

        else:
            cur.execute('SELECT `user_id`, `user_name` from `users` WHERE `user_info`=?', (message.text,))
            user_info = cur.fetchone()
            conn.commit()

        if user_info:
            await message.answer(f'<b>Информация о пользователе</b>\n'
                                 f'Username: {user_info[1]}\n'
                                 f'User ID: {user_info[0]}\n',
                                 parse_mode='HTML')
            await state.finish()

        else:
            await message.reply('Пользователя с такими данными не существует в базе данных. '
                                'Проверьте правильность введённых данных и попробуйте снова.')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def command_block(message: Message):

    try:
        global admins_ID
        if message.from_user.id not in admins_ID:
            admins_ID.append(message.from_user.id)

        await FSMActions.block.set()
        await message.answer(f'Введите USER ID пользователя, которого хотите заблокировать{emoji.emojize(":down_arrow:")}')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def blocking_user(message: Message, state: FSMContext):

    try:
        cur.execute('SELECT * from `users` WHERE `user_id`=?', (message.text,))
        user_info = cur.fetchone()
        conn.commit()

        if user_info:
            cur.execute('UPDATE `users` SET `is_block`=? WHERE `user_id`=?', (True, message.text))
            conn.commit()
            await message.reply(f'Данный пользователь заблокирован!{emoji.emojize(":check_mark:")}')
            await bot.send_message(chat_id=user_info[1], text='Вы были заблокированы администратором',
                                   reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            await message.reply('Пользователя с таким USER ID не существует в базе данных. '
                                'Проверьте правильность введённых данных и попробуйте снова.')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def command_unblock(message: Message):
    try:
        global admins_ID
        if message.from_user.id not in admins_ID:
            admins_ID.append(message.from_user.id)

        await FSMActions.unblock.set()
        await message.answer(f'Введите USER ID пользователя, которого хотите разблокировать{emoji.emojize(":down_arrow:")}')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def unblocking_user(message: Message, state: FSMContext):

    try:
        cur.execute('SELECT * from `users` WHERE `user_id`=?', (message.text,))
        user_info = cur.fetchone()
        conn.commit()

        if user_info:
            cur.execute('UPDATE `users` SET `is_block`=? WHERE `user_id`=?', (False, message.text))
            conn.commit()
            await message.reply(f'Данный пользователь разблокирован!{emoji.emojize(":check_mark:")}')
            await bot.send_message(chat_id=user_info[1], text='Вы были разблокированы администратором',
                                   reply_markup=main_menu_kb)
            await state.finish()
        else:
            await message.reply('Пользователя с таким USER ID не существует в базе данных. '
                                'Проверьте правильность введённых данных и попробуйте снова.')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def callback_answer_or_ignore(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == 'Ответить':
            await FSMActions.answer.set()
            async with state.proxy() as data:
                data['chat_id'] = callback.from_user.id
            await callback.message.reply(f'Напишите текст ответа <b>одним</b> сообщением{emoji.emojize(":down_arrow:")}',
                                         parse_mode='HTML')

        elif callback.data == 'Игнорировать':
            await callback.message.edit_reply_markup(reply_markup=None)

    except:
        await callback.message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_answer(message: Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            await bot.send_message(chat_id=data['chat_id'], text=f'<b>Ответ администратора:</b>\n\n{message.text}',
                                   parse_mode='HTML')
        await state.finish()

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def cancel_by_command(message: Message, state: FSMContext):

    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()

        await check_admin(message=message)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(check_admin, commands=['admin'], is_chat_admin=True)
    dp.register_message_handler(get_chat_id, commands=['chat_id'], is_chat_admin=True)
    dp.register_message_handler(command_info_user, commands=['info_user'], is_chat_admin=True)
    dp.register_message_handler(command_spam, commands=['spam'], is_chat_admin=True)
    dp.register_message_handler(command_block, commands=['block'], is_chat_admin=True)
    dp.register_message_handler(command_unblock, commands=['unblock'], is_chat_admin=True)
    dp.register_message_handler(cancel_by_command,
                                commands=['admin', 'chat_id', 'info_user', 'spam', 'block', 'unblock'],
                                state=[FSMActions.info_choice,
                                       FSMActions.info_param,
                                       FSMActions.spam,
                                       FSMActions.block,
                                       FSMActions.unblock])
    dp.register_callback_query_handler(viewing_user_info_by, state=FSMActions.info_choice)
    dp.register_message_handler(viewing_user_info, state=FSMActions.info_param)
    dp.register_message_handler(making_spam, state=FSMActions.spam)
    dp.register_message_handler(blocking_user, state=FSMActions.block)
    dp.register_message_handler(unblocking_user, state=FSMActions.unblock)
    dp.register_callback_query_handler(callback_answer_or_ignore, Text(startswith=['Ответить', 'Игнорировать']))
    dp.register_message_handler(get_answer, state=FSMActions.answer)
