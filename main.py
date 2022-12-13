from loader import dp
from aiogram.utils import executor

from handlers import client_start, client_application, client_useful_contacts, client_settings, client_contact
from handlers import admin


if __name__ == '__main__':

    client_start.register_handlers_client(dp=dp)
    client_application.register_handlers_client_application(dp=dp)
    client_useful_contacts.register_handlers_client_useful_contacts(dp=dp)
    client_settings.register_handlers_client_settings(dp=dp)
    client_contact.register_handlers_client_contact(dp=dp)

    admin.register_handlers_admin(dp=dp)

    executor.start_polling(dp, skip_updates=True)
