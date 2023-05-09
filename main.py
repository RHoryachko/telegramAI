import os
import telebot
import speech_recognition as sr

from io import BytesIO
from pydub import AudioSegment
from CONFIG import TELEGRAM_API_TOKEN
from clientAI import answer



bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
recognizer = sr.Recognizer()



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю я AI telegram Bot. Можеш задавати мені питання")



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

