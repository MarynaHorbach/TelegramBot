from pathlib import Path
import googletrans
import aiogram
from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from gtts import gTTS
from aiogram.dispatcher.filters.state import State, StatesGroup
import speech_recognition as sr
import soundfile as sf
from pydub import AudioSegment

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

token = os.environ.get('token')

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())
lang_index = 'en'
operation_ind = 'translate'

help_message = "Hi! This bot is for translating, converting text to audio and transcribing (except apple) messages. Choose an option and follow the instructions (you will be able to choose a language).\n^-^\nFor next action press 'next'"


class Form(StatesGroup):
    text_to_pr = State()


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Translate"),
            types.KeyboardButton(text="Convert into audio"),
            types.KeyboardButton(text="Transcribe")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Choose what to do"
    )
    await message.answer(
        help_message,
        reply_markup=keyboard)


@dp.message_handler(commands=['next'])
async def next_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Translate"),
            types.KeyboardButton(text="Convert into audio"),
            types.KeyboardButton(text="Transcribe")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Choose what to do"
    )
    await message.answer(
        help_message,
        reply_markup=keyboard)


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Translate"))
async def choosing_lang(message: types.Message):
    global operation_ind
    operation_ind = 'translate'
    huge_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    huge_kb.add('ru', 'en', 'be')
    huge_kb.add('uk', 'pl', 'kk')
    huge_kb.add('fr', 'eo', 'tr')
    huge_kb.add('/help', '/next')
    await message.answer(
        "Choose a language:\nru - russian\nen - english\nbe - belarussian\nuk - ukrainian\npl - polish\nkk - kazakh\nfr - french\neo - esperanto\ntr - turkish",
        reply_markup=huge_kb)


@dp.message_handler(aiogram.dispatcher.filters.Text(equals=['ru', 'en', 'be', 'uk', 'pl', 'kk', 'fr', 'eo', 'tr']))
async def translation_res_send(message: types.Message):
    global lang_index
    lang_index = message.text
    global operation_ind
    if operation_ind == 'translate' or operation_ind == 'convert_to_audio':
        await Form.text_to_pr.set()
        await message.reply("Send your text")
    elif operation_ind == 'transcribe':
        await message.reply("Send your voice message or audio file (it should be longer than 5 seconds)\nRemember that function is not available on apple.")


@dp.message_handler(state=Form.text_to_pr)
async def translation_res_send(message: types.Message, state: FSMContext):
    global lang_index
    lang = lang_index
    if operation_ind == 'translate':
        await state.finish()
        if message.text == "/help":
            kb = [
                [
                    types.KeyboardButton(text="Translate"),
                    types.KeyboardButton(text="Convert into audio"),
                    types.KeyboardButton(text="Transcribe")
                ],
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder="Choose what to do"
            )
            await message.answer(help_message,
                                 reply_markup=keyboard)
        else:
            res = translate_text_to_lang(message.text, lang)
            await message.reply(res)
    elif operation_ind == 'convert_to_audio':
        await state.finish()
        if message.text == "/help":
            kb = [
                [
                    types.KeyboardButton(text="Translate"),
                    types.KeyboardButton(text="Convert into audio"),
                    types.KeyboardButton(text="Transcribe")
                ],
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder="Choose what to do"
            )
            await message.answer(
                help_message, reply_markup=keyboard)
        else:
            var = gTTS(text=message.text, lang=lang)
            var.save('eng.mp3')
            await bot.send_audio(message.chat.id, open("eng.mp3", "rb"), performer="Performer", title="Title")


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Convert into audio"))
async def choosing_lang(message: types.Message):
    global operation_ind
    operation_ind = 'convert_to_audio'
    huge_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    huge_kb.add('ru', 'en', 'pl')
    huge_kb.add('fr', 'tr', 'uk')
    huge_kb.add('/help', '/next')

    await message.answer(
        "Choose a language:\nru - russian\nen - english\nbe - belarussian\nuk - ukrainian\npl - polish\nkk - kazakh\nfr - french\neo - esperanto\ntr - turkish",
        reply_markup=huge_kb)


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Transcribe"))
async def transcription(message: types.Message):
    global operation_ind
    operation_ind = 'transcribe'
    huge_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    huge_kb.add('ru', 'en')
    huge_kb.add('/help', '/next')

    await message.answer(
        "Choose a language:\nru - russian\nen - english",
        reply_markup=huge_kb)


@dp.message_handler(content_types=[
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
]
)
async def voice_message_handler(message: types.Message):
    global lang_index
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Wrong format(")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    if file_path[-4:] == ".mp3":
        file_on_disk = Path("", "temp.mp3")
        await bot.download_file(file_path, destination=file_on_disk)
        await message.reply("Received. Please, wait for a bit)")
        sound = AudioSegment.from_mp3("temp.mp3")
        sound.export("temp.wav", format="wav")

        try:
            r = sr.Recognizer()
            user_audio_file = sr.AudioFile("temp.wav")
            with user_audio_file as source:
                user_audio = r.record(source)
            text = r.recognize_google(user_audio, language=lang_index)
            await message.reply(text)
        except:
            await message.reply("Sorry... It's too hard to transcribe (or too short)")

    elif file_path[-4:] == ".wav":
        file_on_disk = Path("", "temp.wav")
        await bot.download_file(file_path, destination=file_on_disk)
        await message.reply("Received. Please, wait for a bit)")

        try:
            r = sr.Recognizer()
            user_audio_file = sr.AudioFile("temp.wav")
            with user_audio_file as source:
                user_audio = r.record(source)
            text = r.recognize_google(user_audio, language=lang_index)
            await message.reply(text)
        except:
            await message.reply("Sorry... It's too hard to transcribe (or too short)")

    else:
        await message.reply("Wrong format, try mp3, wav or voice message.")


@dp.message_handler(content_types=[
    types.ContentType.VOICE
]
)
async def voice_message_handler(message: types.Message):
    global lang_index
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    else:
        await message.reply("Wrong format(")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    if file_path[-4:] == ".oga":
        file_on_disk = Path("", "temp.oga")
        await bot.download_file(file_path, destination=file_on_disk)

        await message.reply("Received. Please, wait for a bit)")
        try:
            data, samplerate = sf.read('temp.oga')
            sf.write('temp.wav', data, samplerate)
            r = sr.Recognizer()
            user_audio_file = sr.AudioFile("temp.wav")
            with user_audio_file as source:
                user_audio = r.record(source)
            text = r.recognize_google(user_audio, language=lang_index)
            await message.reply(text)
        except:
            await message.reply("Sorry... It's too hard to transcribe (or too short)")
    elif file_path[-4:] == ".ogg":
        file_on_disk = Path("", "temp.ogg")
        await bot.download_file(file_path, destination=file_on_disk)

        await message.reply("Received. Please, wait for a bit)")
        try:
            data, samplerate = sf.read('temp.ogg')
            sf.write('temp.wav', data, samplerate)
            r = sr.Recognizer()
            user_audio_file = sr.AudioFile("temp.wav")
            with user_audio_file as source:
                user_audio = r.record(source)
            text = r.recognize_google(user_audio, language=lang_index)
            await message.reply(text)
        except:
            await message.reply("Sorry... It's too hard to transcribe (or too short)")
    else:
        await message.reply("Wrong format(")



def translate_text_to_lang(message, lang):
    translator = googletrans.Translator()
    ans = translator.translate(message, lang)
    return ans.text


@dp.message_handler()
async def just_wrong_text(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Translate"),
            types.KeyboardButton(text="Convert into audio"),
            types.KeyboardButton(text="Transcribe")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Choose what to do"
    )
    await message.answer(
        "Please follow the instructions",
        reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
