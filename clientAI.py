import os
import openai
import requests
import sqlite3
import json

from CONFIG import OPENAI_API_KEY, TELEGRAM_API_TOKEN


openai.api_key = OPENAI_API_KEY




def answer(prompt, chat_id):
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

    # bot.send_chat_action(chat_id, 'typing')

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

    # Close the connection before returning the response
    conn.close()

    return chat_response
