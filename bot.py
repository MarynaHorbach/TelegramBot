import googletrans
import aiogram
from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from gtts import gTTS
from playsound import playsound
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

token = os.environ.get('token')

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())
lang_index = 'en'
operation_ind = 'translate'


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
        "Hi! This bot is for translating and transcribing messages.\nFor transcribing press 'Transcribe' and follow the instructions.\nFor translating press 'Translate' and follow the instructions (you will be able to choose a language).\n^-^",
        reply_markup=keyboard)


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Translate"))
async def choosing_lang(message: types.Message):
    global operation_ind
    operation_ind = 'translate'
    huge_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    huge_kb.add('ru', 'en', 'be')
    huge_kb.add('uk', 'pl', 'kk')
    huge_kb.add('fr', 'eo', 'tr')
    huge_kb.add('/help')
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
            await message.answer(
                "Hi! This bot is for translating and transcribing messages.\nFor transcribing press 'Transcribe' and follow the instructions.\nFor translating press 'Translate' and follow the instructions (you will be able to choose a language).\n^-^",
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
                "Hi! This bot is for translating and transcribing messages.\nFor transcribing press 'Transcribe' and follow the instructions.\nFor translating press 'Translate' and follow the instructions (you will be able to choose a language).\n^-^",
                reply_markup=keyboard)
        else:
            var = gTTS(text=message.text, lang=lang)
            var.save('eng.mp3')
            await bot.send_audio(message.from_user.id, open("eng.mp3", "rb"), performer="Performer", title="Title")


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Convert into audio"))
async def choosing_lang(message: types.Message):
    global operation_ind
    operation_ind = 'convert_to_audio'
    huge_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    huge_kb.add('ru', 'en', 'pl')
    huge_kb.add('fr', 'tr', 'uk')
    huge_kb.add('/help')

    await message.answer(
        "Choose a language:\nru - russian\nen - english\nbe - belarussian\nuk - ukrainian\npl - polish\nkk - kazakh\nfr - french\neo - esperanto\ntr - turkish",
        reply_markup=huge_kb)


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Transcribe"))
async def transcription(message: types.Message):
    await message.reply("Will be implemented soon")


def translate_text_to_lang(message, lang):
    translator = googletrans.Translator()
    ans = translator.translate(message, lang)
    return ans.text


if __name__ == '__main__':
    executor.start_polling(dp)
