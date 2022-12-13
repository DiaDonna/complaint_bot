from loader import bot
from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.exceptions import BadRequest

from config_data.config import APPLICATIONS_GROUP_ID, OFFERS_GROUP_ID
from database.db_loader import cur, conn

from keyboards.reply.main_menu import main_menu_kb
from keyboards.inline.application_category import application_category_kb
from keyboards.inline.pass_or_back import pass_or_back_kb
from keyboards.inline.back_only import back_only_kb

import emoji


class FSMApplication(StatesGroup):
    category = State()
    address_complaint = State()
    photo_complaint = State()
    reason_complaint = State()


class FSMOffer(StatesGroup):
    description_offer = State()


async def application_from_main_menu(message: Message):

    try:
        await FSMApplication.category.set()
        await bot.send_message(message.chat.id,
                               f'{emoji.emojize(":name_badge::backhand_index_pointing_down::name_badge:")}'
                               f'_Выберите категорию, по которой Вы хотите оставить заявку в УК:_',
                               parse_mode='Markdown',
                               reply_markup=application_category_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_application_category(callback: CallbackQuery, state: FSMContext):

    try:
        if callback.data == 'Заявка':
            await callback.message.delete()
            await FSMApplication.address_complaint.set()
            await bot.send_message(callback.message.chat.id,
                                   f'*Шаг 1/3.*{emoji.emojize(":memo:")}Напишите адрес или ориентир проблемы (улицу, номер '
                                   f'дома, подъезд, этаж и квартиру) или пропустите этот пункт:',
                                   parse_mode='Markdown',
                                   reply_markup=pass_or_back_kb)

        elif callback.data == 'Предложение':
            await callback.message.delete()
            await state.finish()
            await FSMOffer.description_offer.set()
            await bot.send_message(callback.message.chat.id,
                                   f'{emoji.emojize(":memo:")}*Распишите ваше предложение в подробностях: (Добавьте '
                                   f'фотографию, если есть)*',
                                   parse_mode='Markdown',
                                   reply_markup=back_only_kb)

        elif callback.data == 'Назад':
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


async def get_address(message: Message, state: FSMContext, from_back: bool = False):

    try:
        if not from_back:
            async with state.proxy() as data:
                data['address'] = message.text

        await FSMApplication.photo_complaint.set()
        await bot.send_message(message.chat.id,
                               f'*Шаг 2/3.*{emoji.emojize(":framed_picture:")}Прикрепите фотографию или видео к своей '
                               f'заявке или пропустите этот пункт:',
                               parse_mode='Markdown',
                               reply_markup=pass_or_back_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_photo_or_video(message: Message, state: FSMContext, from_back: bool = False):
    try:
        if not from_back:
            if message.photo or message.video:
                if message.photo:
                    async with state.proxy() as data:
                        data['media_id'] = message.photo[0].file_id
                elif message.video:
                    async with state.proxy() as data:
                        data['media_id'] = message.video.file_id

            else:
                await bot.send_message(message.chat.id,
                                       f'{emoji.emojize(":no_entry::name_badge:")}В данном пункте нужно обязательно '
                                       f'отправить *фотографию* или *видео* в виде медиа-сообщения. *Попробуйте ещё раз:*',
                                       parse_mode='Markdown')

        await FSMApplication.reason_complaint.set()
        await bot.send_message(message.chat.id,
                               f'*Шаг 3/3.*{emoji.emojize(":name_badge:")}Напишите причину обращения в '
                               f'подробностях:',
                               parse_mode='Markdown',
                               reply_markup=back_only_kb)

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_reason(message: Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            data['reason'] = message.text
        await bot.send_message(message.chat.id,
                               f'{emoji.emojize(":check_mark_button:")}*Жалоба отправлена администрации.* _Спасибо за Ваше '
                               f'обращение!_',
                               parse_mode='Markdown')

        # Делаем запрос к БД по user_id
        cur.execute('SELECT * FROM `users` WHERE `user_id`=?', (message.from_user.id,))
        user_info = cur.fetchone()
        conn.commit()

        # Формируем отправку сообщения в группу жалоб (с фото/с видео/без медиа)
        text_for_group = f'{emoji.emojize(":no_entry:")}<b>Поступила новая жалоба:</b> @{user_info[2]}\n' \
                         f'<b>Имя и Фамилия:</b> {user_info[3]}\n' \
                         f'<b>Номер телефона:</b> {user_info[4]}\n' \
                         f'<b>Адрес:</b> {data["address"]}\n' \
                         f'<b>Содержание:</b> {data["reason"]}'

        if data['media_id'] != '-':
            try:
                await bot.send_photo(chat_id=APPLICATIONS_GROUP_ID,
                                     photo=data['media_id'],
                                     caption=text_for_group,
                                     parse_mode='HTML')
            except BadRequest:
                await bot.send_video(chat_id=APPLICATIONS_GROUP_ID,
                                     video=data['media_id'],
                                     caption=text_for_group,
                                     parse_mode='HTML')
        else:
            await bot.send_message(chat_id=APPLICATIONS_GROUP_ID,
                                   text=text_for_group,
                                   parse_mode='HTML')

        await state.finish()

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def get_offer_description(message: Message, state: FSMContext):

    try:
        if message.text or (message.photo and message.caption):
            if message.text:
                async with state.proxy() as data:
                    data['description'] = message.text
                    data['description_media'] = '-'
            elif message.photo and message.caption:
                async with state.proxy() as data:
                    data['description'] = message.caption
                    data['description_media'] = message.photo[0].file_id
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":check_mark_button::memo:")}*Идея принята и передана администрации* '
                                   f'_Спасибо за Ваше обращение!_',
                                   parse_mode='Markdown')

            # Делаем запрос к БД по user_id
            cur.execute('SELECT * FROM `users` WHERE `user_id`=?', (message.from_user.id,))
            user_info = cur.fetchone()
            conn.commit()

            # Формируем отправку сообщения в группу предложений (с фото/без фото)
            text_for_group = f'{emoji.emojize(":memo:")}<b>Поступило новое предложение:</b> @{user_info[2]}\n' \
                             f'<b>Имя и Фамилия:</b> {user_info[3]}\n' \
                             f'<b>Номер телефона:</b> {user_info[4]}\n' \
                             f'<b>Содержание:</b> {data["description"]}'

            if data['description_media'] != '-':
                await bot.send_photo(chat_id=OFFERS_GROUP_ID,
                                     photo=data['description_media'],
                                     caption=text_for_group,
                                     parse_mode='HTML')
            else:
                await bot.send_message(chat_id=OFFERS_GROUP_ID,
                                       text=text_for_group,
                                       parse_mode='HTML')

            await state.finish()

        elif message.photo:
            await bot.send_message(message.chat.id,
                                   f'{emoji.emojize(":no_entry::name_badge:")}Предложение должно содержать только текст')

    except:
        await message.answer('Что-то пошло не так. Пожалуйста, выберите команду заново.')


async def callback_for_pass_or_back(callback: CallbackQuery, state: FSMContext):

    try:
        current_state = await state.get_state()

        if callback.data == 'Пропустить':

            if current_state == FSMApplication.address_complaint.state:
                await bot.delete_message(callback.message.chat.id, callback.message.message_id)
                async with state.proxy() as data:
                    data['address'] = '-'
                await get_address(message=callback.message, state=FSMApplication.address_complaint.state,
                                  from_back=True)

            elif current_state == FSMApplication.photo_complaint.state:
                await bot.delete_message(callback.message.chat.id, callback.message.message_id)
                async with state.proxy() as data:
                    data['media_id'] = '-'
                await get_photo_or_video(message=callback.message, state=FSMApplication.photo_complaint.state,
                                         from_back=True)

            elif current_state == FSMApplication.reason_complaint.state:
                await bot.delete_message(callback.message.chat.id, callback.message.message_id)
                async with state.proxy() as data:
                    data['reason'] = 'не указана'
                await get_reason(message=callback.message, state=FSMApplication.reason_complaint.state)

        elif callback.data == 'Назад':
            if current_state in [FSMApplication.address_complaint.state,
                                 FSMApplication.photo_complaint.state,
                                 FSMApplication.reason_complaint.state,
                                 FSMOffer.description_offer.state]:
                await bot.delete_message(callback.message.chat.id, callback.message.message_id)
                await application_from_main_menu(message=callback.message)

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


def register_handlers_client_application(dp: Dispatcher):
    dp.register_message_handler(application_from_main_menu,
                                Text(endswith='Оставить заявку'),
                                state=None)
    dp.register_message_handler(cancel_by_command_menu,
                                commands=['menu'],
                                state='*')
    dp.register_callback_query_handler(get_application_category,
                                       state=FSMApplication.category)
    dp.register_callback_query_handler(callback_for_pass_or_back,
                                       Text(endswith=['Пропустить', 'Назад']),
                                       state='*')
    dp.register_message_handler(get_address,
                                state=FSMApplication.address_complaint)
    dp.register_message_handler(get_photo_or_video,
                                content_types=['photo', 'video', 'voice', 'document', 'video_note', 'sticker'],
                                state=FSMApplication.photo_complaint)
    dp.register_message_handler(get_reason,
                                state=FSMApplication.reason_complaint)
    dp.register_message_handler(get_offer_description,
                                content_types=['text', 'photo'],
                                state=FSMOffer.description_offer)
