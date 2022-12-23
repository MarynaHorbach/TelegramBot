import googletrans
import aiogram
from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

token = os.environ.get('token')

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())
lang_index = 'en'


class Form(StatesGroup):
    text_to_pr = State()


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Translate"),
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
    huge_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    huge_kb.add('ru', 'en', 'be')
    huge_kb.add('uk', 'pl', 'kk')
    huge_kb.add('fr', 'eo', 'tr')

    await message.answer(
        "Choose a language:\nru - russian\nen - english\nbe - belarussian\nuk - ukrainian\npl - polish\nkk - kazakh\nfr - french\neo - esperanto\ntr - turkish",
        reply_markup=huge_kb)


@dp.message_handler(aiogram.dispatcher.filters.Text(equals=['ru', 'en', 'be', 'uk', 'pl', 'kk', 'fr', 'eo', 'tr']))
async def translation_res_send(message: types.Message):
    global lang_index
    lang_index = message.text
    print("Hi")
    await Form.text_to_pr.set()
    await message.reply("Send your text")


@dp.message_handler(state=Form.text_to_pr)
async def translation_res_send(message: types.Message, state: FSMContext):
    global lang_index
    lang = lang_index
    print("Hi")
    print(lang)
    await state.finish()
    res = translate_text_to_lang(message.text, lang)
    print(res)
    await message.reply(res)


# @dp.message_handler()
# async def process_name(message: types.Message, state: FSMContext):
#     """Process user name"""
#
#     # Finish our conversation
#
#     await message.reply(f"Hello, {message.text}")


@dp.message_handler(aiogram.dispatcher.filters.Text(equals="Transcribe"))
async def transcription(message: types.Message):
    await message.reply("Will be implemented soon")


# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):
#     if message.text == "/help":
#         bot.send_message(message.from_user.id,
#                          "For transcribing press 'Transcribe' and follow the instructions.\nFor translating press 'Translate' and follow the instructions (you will be able to choose a language).\n^-^")
#     elif message.text == "Translate":
#         bot.send_message(message.from_user.id, "Choose a language you want to translate to")
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='russian', callback_data=1))
#         markup.add(telebot.types.InlineKeyboardButton(text='english', callback_data=2))
#         # markup.add(telebot.types.InlineKeyboardButton(text='belarusian', callback_data=3))
#         # markup.add(telebot.types.InlineKeyboardButton(text='esperanto', callback_data=4))
#         # markup.add(telebot.types.InlineKeyboardButton(text='french', callback_data=5))
#         # markup.add(telebot.types.InlineKeyboardButton(text='kazakh', callback_data=6))
#         # markup.add(telebot.types.InlineKeyboardButton(text='ukrainian', callback_data=7))
#         # markup.add(telebot.types.InlineKeyboardButton(text='polish', callback_data=8))
#     elif message.text == "Change language":
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='russian', callback_data=1))
#         markup.add(telebot.types.InlineKeyboardButton(text='english', callback_data=2))
#         markup.add(telebot.types.InlineKeyboardButton(text='belarusian', callback_data=3))
#         markup.add(telebot.types.InlineKeyboardButton(text='esperanto', callback_data=4))
#         markup.add(telebot.types.InlineKeyboardButton(text='french', callback_data=5))
#         markup.add(telebot.types.InlineKeyboardButton(text='kazakh', callback_data=6))
#         markup.add(telebot.types.InlineKeyboardButton(text='ukrainian', callback_data=7))
#         markup.add(telebot.types.InlineKeyboardButton(text='polish', callback_data=8))
#     elif message.text == "Transcribe":
#         bot.send_message(message.from_user.id, "Send your text")
#         # doing smth
#     else:
#         bot.send_message(message.from_user.id, "I don't understand you :( Try using /help.")
#
#
def translate_text_to_lang(message, lang):
    translator = googletrans.Translator()
    ans = translator.translate(message, lang)
    return ans.text


#
#
# @bot.callback_query_handler(func=lambda call: True)
# def query_handler(call):
#     bot.answer_callback_query(callback_query_id=call.id)
#     if call.data == '1':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'ru')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '2':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'en')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '3':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'be')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '4':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'eo')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '5':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'fr')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '6':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'kk')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '7':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'uk')
#         bot.send_message(message.from_user.id, res)
#     elif call.data == '8':
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Change language'))
#         message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                         text="Send your text", reply_markup=markup)
#         res = translate_text_to_lang(message.text, 'pl')
#         bot.send_message(message.from_user.id, res)
#
#
if __name__ == '__main__':
    executor.start_polling(dp)
