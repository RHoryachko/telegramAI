import os
import telebot
import openai
import requests
import speech_recognition as sr
from io import BytesIO
from pydub import AudioSegment
from CONFIG import OPENAI_API_KEY, TELEGRAM_API_TOKEN


openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
recognizer = sr.Recognizer()

# Словник для зберігання історії чатів
chat_histories = {}

def answer(prompt, chat_id):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []

    chat_history = chat_histories[chat_id]

    if len(chat_history) > 5:
        chat_history.pop(0)

    chat_history.append({"role": "user", "content": prompt})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    chat_response = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": chat_response})
    return chat_response

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
        response_text = answer(text, message.chat.id)
        bot.send_message(message.chat.id, response_text)
    except sr.UnknownValueError:
        bot.reply_to(message, 'Вибачте, я не зміг розпізнати ваше голосове повідомлення.')

bot.polling(none_stop=True)

