import os
import openai
import requests
import sqlite3
import json
import time



def update_tokens(api_key, tokens_to_add):
    conn = sqlite3.connect('DataBase/chat_history.db')
    c = conn.cursor()

    # Отримання поточних значень tokens_used та tokens для ключа api_key
    c.execute("SELECT tokens_used, tokens FROM apiKeys WHERE key=?", (api_key,))
    row = c.fetchone()

    if row is None:
        print("Invalid API key.")
    else:
        tokens_used, tokens = row
        new_tokens_used = tokens_used + tokens_to_add
        new_tokens = tokens - tokens_to_add

        # Оновлення значень tokens_used та tokens в таблиці apiKeys
        c.execute("UPDATE apiKeys SET tokens_used=?, tokens=? WHERE key=?", (new_tokens_used, new_tokens, api_key))

    conn.commit()
    conn.close()



def checkKey():
    conn = sqlite3.connect('DataBase/chat_history.db')
    c = conn.cursor()

    # Запит на отримання всіх активних ключів з total_tokens менше 200
    c.execute("SELECT * FROM apiKeys WHERE valid = 1 AND tokens_used > 7500000")
    keys_to_deactivate = c.fetchall()

    # Деактивація ключів, які мають менше 200 total_tokens
    for key in keys_to_deactivate:
        c.execute("UPDATE apiKeys SET valid=? WHERE key=?", (False, key[0]))

    conn.commit()
    conn.close()



def getKey():
    current_time_millis = int(time.time() * 1000)

    conn = sqlite3.connect('DataBase/chat_history.db')
    c = conn.cursor()

    c.execute("SELECT * FROM apiKeys WHERE valid = 1 ORDER BY last_used ASC LIMIT 1")
    row = c.fetchone()

    if row is None:
        return None
    else:
        key = row[0]
        c.execute("UPDATE apiKeys SET last_used=? WHERE key=?", (current_time_millis, key))
        conn.commit()
        conn.close()
        return key




def answer(prompt, chat_id):

    checkKey()

    openai.api_key = getKey()

    # Connect to the SQLite3 database inside the answer function
    conn = sqlite3.connect('DataBase/chat_history.db')
    c = conn.cursor()

    c.execute("SELECT history FROM chat_history WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    if row is None:
        chat_history = []
        c.execute("INSERT INTO chat_history (chat_id, history) VALUES (?, ?)", (chat_id, json.dumps(chat_history)))
        conn.commit()
    else:
        chat_history = json.loads(row[0])

    chat_history.append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )


    chat_response = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": chat_response})
    
    # Remove the first 2 messages if there are more than 10 messages in the chat history
    while len(chat_history) > 10:
        chat_history.pop(0)
        chat_history.pop(0)

    # Update the chat history in the database
    c.execute("UPDATE chat_history SET history=? WHERE chat_id=?", (json.dumps(chat_history), chat_id))
    conn.commit()

    total_tokens = completion['usage']['total_tokens']
    print(total_tokens)
    update_tokens(openai.api_key, total_tokens)

    # Close the connection before returning the response
    conn.close()

    return chat_response
