import os
import telebot
import speech_recognition as sr

from io import BytesIO
from pydub import AudioSegment
from CONFIG import OPENAI_API_KEY, TELEGRAM_API_TOKEN
from clientAI import answer



bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
recognizer = sr.Recognizer()



# def answer(prompt, chat_id):
#     # Connect to the SQLite3 database inside the answer function
#     conn = sqlite3.connect('DataBase/chat_history.db')
#     c = conn.cursor()

#     c.execute("SELECT history FROM chat_history WHERE chat_id=?", (chat_id,))
#     row = c.fetchone()
#     if row is None:
#         chat_history = []
#         c.execute("INSERT INTO chat_history (chat_id, history) VALUES (?, ?)", (chat_id, json.dumps(chat_history)))
#         conn.commit()
#     else:
#         chat_history = json.loads(row[0])

#     chat_history.append({"role": "user", "content": prompt})

#     # bot.send_chat_action(chat_id, 'typing')

#     completion = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=chat_history
#     )


#     chat_response = completion.choices[0].message.content
#     chat_history.append({"role": "assistant", "content": chat_response})
    
#     # Remove the first 2 messages if there are more than 10 messages in the chat history
#     while len(chat_history) > 10:
#         chat_history.pop(0)
#         chat_history.pop(0)

#     # Update the chat history in the database
#     c.execute("UPDATE chat_history SET history=? WHERE chat_id=?", (json.dumps(chat_history), chat_id))
#     conn.commit()

#     # Close the connection before returning the response
#     conn.close()

#     return chat_response



@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text:
        print(message.text)
        bot.send_chat_action(message.chat.id, 'typing')
        responce_text = answer(message.text, message.chat.id)
        bot.send_message(message.chat.id, responce_text)



@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    voice_info = bot.get_file(message.voice.file_id)
    voice_file_url = f'https://api.telegram.org/file/bot{TELEGRAM_API_TOKEN}/{voice_info.file_path}'
    response = requests.get(voice_file_url)
    voice_file = BytesIO(response.content)

    with open("voice/temp_voice.ogg", "wb") as temp_ogg:
        temp_ogg.write(voice_file.read())
        temp_ogg.flush()

    ogg_audio = AudioSegment.from_file("voice/temp_voice.ogg", format="ogg", codec="opus")
    ogg_audio.export("voice/temp_voice.wav", format="wav")

    with sr.AudioFile("voice/temp_voice.wav") as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language='uk')
        print(text)

        bot.send_chat_action(message.chat.id, 'typing')
        
        response_text = answer(text, message.chat.id)
        bot.send_message(message.chat.id, response_text)
    except sr.UnknownValueError:
        bot.reply_to(message, 'Вибачте, я не зміг розпізнати ваше голосове повідомлення.')




bot.polling(none_stop=True)

