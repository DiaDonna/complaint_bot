from dotenv import load_dotenv, find_dotenv
import os

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
APPLICATIONS_GROUP_ID = os.getenv('APPLICATIONS_GROUP_CHAT_ID')
OFFERS_GROUP_ID = os.getenv('OFFERS_GROUP_CHAT_ID')
ADMIN_GROUP_ID = os.getenv('ADMIN_GROUP_CHAT_ID')

