import os
import sqlite3
import json

#Перевірка на наявність директорії
database_folder = "../DataBase"
if not os.path.exists(database_folder):
    os.makedirs(database_folder)

# Створення БД
conn = sqlite3.connect('../DataBase/chat_history.db')

# Створення курсору
c = conn.cursor()

# Створення таблиці
c.execute('''CREATE TABLE IF NOT EXISTS chat_history
             (chat_id INTEGER PRIMARY KEY, history TEXT)''')

# Закриття БД
conn.commit()
conn.close()