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
c.execute('''CREATE TABLE IF NOT EXISTS apiKeys
             (key TEXT PRIMARY KEY, tokens_used INTEGER, 
             valid BOOLEAN, tokens INTEGER, last_used INTEGER)''')

print("Created Chat Keys DB")

# Закриття БД
conn.commit()
conn.close()