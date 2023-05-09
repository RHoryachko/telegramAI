import telebot
import sqlite3
import time

from telebot import types
from CONFIG import TELEGRAM_ADMIN_TOKEN


bot = telebot.TeleBot(TELEGRAM_ADMIN_TOKEN)



@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == 590333501:
    	bot.send_message(message.chat.id, "Адмінка")



@bot.message_handler(commands=['newKey'])
def addKey(message):
    if message.chat.id == 590333501:
    	bot.send_message(message.chat.id, "Введи токен")
    	bot.register_next_step_handler(message, addKey_realization)



def addKey_realization(message):
	if message.text:
		# З'єднання з базою даних
		conn = sqlite3.connect('DataBase/chat_history.db')

		# Створення курсору
		c = conn.cursor()

		api_key = message.text
		tokens_used = 0
		valid = True
		total_tokens = 7500000
		last_used = current_time_millis = int(time.time() * 1000)

		# Вставка запису в таблицю apiKeys
		c.execute("INSERT INTO apiKeys (key, tokens_used, valid, tokens, last_used) VALUES (?, ?, ?, ?, ?)",
          		(api_key, tokens_used, valid, total_tokens, last_used))

		# Збереження змін
		conn.commit()

		print("Inserted API key data into apiKeys table")

		# Закриття з'єднання з базою даних
		conn.close()

		bot.send_message(message.chat.id, "Додано API ключ")



@bot.message_handler(commands=['allKey'])
def allKey(message):
	if message.chat.id == 590333501:

		conn = sqlite3.connect('DataBase/chat_history.db')

	    # Створення курсору
		c = conn.cursor()

	    # Виконання SQL-запиту для вибірки всіх даних з таблиці apiKeys
		c.execute("SELECT * FROM apiKeys")

	    # Отримання всіх рядків результатів
		rows = c.fetchall()

		for row in rows:
			key, tokens_used, valid, tokens, last_used = row
			markup = types.InlineKeyboardMarkup()
			if valid:
				button = types.InlineKeyboardButton(text="Деактивувати", callback_data=f"deactivate_{key}")
			else:
				button = types.InlineKeyboardButton(text="Активувати", callback_data=f"activate_{key}")
			markup.add(button)

			result_str = f"Key: {key}\nTokens used: {tokens_used}\nValid: {valid}\nTokens: {tokens}"
			bot.send_message(message.chat.id, result_str, reply_markup=markup)

	    # Закриття з'єднання з базою даних
		conn.close()




@bot.callback_query_handler(func=lambda call: call.data.startswith("deactivate_") or call.data.startswith("activate_"))
def toggle_activation(call):
    action, key = call.data.split("_")
    new_valid = True if action == "activate" else False

    conn = sqlite3.connect('DataBase/chat_history.db')
    c = conn.cursor()
    c.execute("UPDATE apiKeys SET valid=? WHERE key=?", (new_valid, key))
    conn.commit()
    conn.close()

    # Create a new markup with the updated button text
    new_markup = types.InlineKeyboardMarkup()
    new_button_text = "Активувати" if not new_valid else "Деактивувати"
    new_button = types.InlineKeyboardButton(text=new_button_text, callback_data=f"{action}_{key}")
    new_markup.add(new_button)

    bot.answer_callback_query(call.id, f"Ключ {key} {'активовано' if new_valid else 'деактивовано'}")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)



bot.polling(none_stop=True)

