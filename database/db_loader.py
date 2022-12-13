import sqlite3


# создаем соединение с базой данных SQLite и возвращаем объект, представляющий ее
conn = sqlite3.connect(r'database/database.db', check_same_thread=False)
# создаем объект cursor для SQL-запросов к базе
cur = conn.cursor()
