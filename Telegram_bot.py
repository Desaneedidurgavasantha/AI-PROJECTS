!pip install python-telegram-bot pymongo google-generativeai google-search-results python-dotenv

import os
from dotenv import load_dotenv
from io import StringIO


TELEGRAM_BOT_TOKEN="7791553696:AAGdUzXVfRrlucGskWP8MOpF4i0OPfry55g"
GEMINI_API_KEY="AIzaSyBFuB9e4U1pNP9k9kCPOoiUgw31pO72Iw8"
MONGODB_URI="mongodb://localhost:27017/Durgavasanta"

import logging
import os
import uuid

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaDocument
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from db import DatabaseManager
from gemini_utils import chat_with_gemini, analyze_image
from config import TELEGRAM_BOT_TOKEN
from search_utils import search_web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation states
PHONE_NUMBER = 1
SEARCH_QUERY = 2
FILE_ANALYSIS = 3


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username
    db = DatabaseManager()
    if db.register_user(first_name, username, chat_id):
        keyboard = [[KeyboardButton("Share Phone Number", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Welcome! Please share your phone number.", reply_markup=reply_markup
        )
    else:
        update.message.reply_text("Welcome back!")

def handle_contact(update: Update, context: CallbackContext):
    phone_number = update.message.contact.phone_number
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    db.update_user_phone(chat_id, phone_number)
    update.message.reply_text("Thank you, your phone number has been saved.")

def chat_handler(update: Update, context: CallbackContext):
    user_input = update.message.text
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    response = chat_with_gemini(user_input)
    db.save_chat_history(chat_id, "user", user_input)
    db.save_chat_history(chat_id, "bot", response)
    update.message.reply_text(response)


def start_web_search(update: Update, context: CallbackContext):
    update.message.reply_text("Enter your search query:")
    return SEARCH_QUERY

def handle_web_search(update: Update, context: CallbackContext):
    query = update.message.text
    response = search_web(query)
    update.message.reply_text(response)
    return ConversationHandler.END

def file_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    file = None
    file_id = None
    file_name = None
    if update.message.photo:
        file = update.message.photo[-1]
        file_id = file.file_id
        file_name = f"{uuid.uuid4().hex}.jpg"
    elif update.message.document:
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name

    if file:
        file_obj = context.bot.get_file(file_id)
        file_path = os.path.join("files",file_name)
        os.makedirs("files",exist_ok=True)
        file_obj.download(file_path)
        analysis = analyze_image(file_path)
        db.save_file_metadata(chat_id, file_name, analysis)
        update.message.reply_text(analysis)
        return ConversationHandler.END
    else:
        update.message.reply_text("Unsupported file type")


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_contact))

    # Web search conversation handler
    web_search_handler = ConversationHandler(
        entry_points=[CommandHandler("websearch", start_web_search)],
        states={
            SEARCH_QUERY: [MessageHandler(Filters.text & ~Filters.command, handle_web_search)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(web_search_handler)

    #File analysis conversation handler
    file_analysis_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo | Filters.document, file_handler)],
        states={},
        fallbacks=[]
    )
    dispatcher.add_handler(file_analysis_handler)

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
import logging
import os
import uuid

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaDocument
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from db import DatabaseManager
from gemini_utils import chat_with_gemini, analyze_image
from config import TELEGRAM_BOT_TOKEN
from search_utils import search_web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation states
PHONE_NUMBER = 1
SEARCH_QUERY = 2
FILE_ANALYSIS = 3


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username
    db = DatabaseManager()
    if db.register_user(first_name, username, chat_id):
        keyboard = [[KeyboardButton("Share Phone Number", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Welcome! Please share your phone number.", reply_markup=reply_markup
        )
    else:
        update.message.reply_text("Welcome back!")

def handle_contact(update: Update, context: CallbackContext):
    phone_number = update.message.contact.phone_number
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    db.update_user_phone(chat_id, phone_number)
    update.message.reply_text("Thank you, your phone number has been saved.")

def chat_handler(update: Update, context: CallbackContext):
    user_input = update.message.text
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    response = chat_with_gemini(user_input)
    db.save_chat_history(chat_id, "user", user_input)
    db.save_chat_history(chat_id, "bot", response)
    update.message.reply_text(response)


def start_web_search(update: Update, context: CallbackContext):
    update.message.reply_text("Enter your search query:")
    return SEARCH_QUERY

def handle_web_search(update: Update, context: CallbackContext):
    query = update.message.text
    response = search_web(query)
    update.message.reply_text(response)
    return ConversationHandler.END

def file_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    file = None
    file_id = None
    file_name = None
    if update.message.photo:
        file = update.message.photo[-1]
        file_id = file.file_id
        file_name = f"{uuid.uuid4().hex}.jpg"
    elif update.message.document:
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name

    if file:
        file_obj = context.bot.get_file(file_id)
        file_path = os.path.join("files",file_name)
        os.makedirs("files",exist_ok=True)
        file_obj.download(file_path)
        analysis = analyze_image(file_path)
        db.save_file_metadata(chat_id, file_name, analysis)
        update.message.reply_text(analysis)
        return ConversationHandler.END
    else:
        update.message.reply_text("Unsupported file type")


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_contact))

    # Web search conversation handler
    web_search_handler = ConversationHandler(
        entry_points=[CommandHandler("websearch", start_web_search)],
        states={
            SEARCH_QUERY: [MessageHandler(Filters.text & ~Filters.command, handle_web_search)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(web_search_handler)

    #File analysis conversation handler
    file_analysis_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo | Filters.document, file_handler)],
        states={},
        fallbacks=[]
    )
    dispatcher.add_handler(file_analysis_handler)

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
MONGODB_DB_NAME="Durga Vasanta"


load_dotenv(stream=StringIO(env_string))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "telegram_bot_db")


# Verify
print(f"Telegram token: {TELEGRAM_BOT_TOKEN}")
print(f"Gemini API key: {GEMINI_API_KEY}")
print(f"MongoDB URI: {MONGODB_URI}")
print(f"MongoDB database name: {MONGODB_DB_NAME}")
print(f"Google search API key: {GOOGLE_SEARCH_API_KEY}")
print(f"Google search CX: {GOOGLE_SEARCH_CX}")

import sys
   from pymongo import MongoClient
   from config import MONGODB_URI, MONGODB_DB_NAME
   from datetime import datetime

   class DatabaseManager:
       def __init__(self):
           self.client = MongoClient(MONGODB_URI)
           self.db = self.client[Durga vasanta]
           self.users = self.db.users
           self.chats = self.db.chats
           self.files = self.db.files

       def register_user(self, first_name, username, chat_id):
           if not self.users.find_one({"chat_id": chat_id}):
               user_data = {"first_name": first_name, "username": username, "chat_id": chat_id, "phone_number": None}
               self.users.insert_one(user_data)
               return True
           return False

       def update_user_phone(self, chat_id, phone_number):
           self.users.update_one({"chat_id": chat_id}, {"$set": {"phone_number": phone_number}})

       def save_chat_history(self, chat_id, role, content):
           chat_data = {
               "chat_id": chat_id,
               "role": role,
               "content": content,
               "timestamp": datetime.utcnow(),
           }
           self.chats.insert_one(chat_data)

       def save_file_metadata(self, chat_id, filename, description):
           file_data = {
               "chat_id": chat_id,
               "filename": filename,
               "description": description,
               "timestamp": datetime.utcnow(),
           }
           self.files.insert_one(file_data)

import google.generativeai as genai
from config import GEMINI_API_KEY
import os

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

image_model = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=generation_config,
    safety_settings=safety_settings
)


def chat_with_gemini(prompt):
    chat = model.start_chat()
    response = chat.send_message(prompt)
    return response.text

def analyze_image(file_path):
    try:
       img = genai.Part.from_file(file_path, mime_type="image/jpeg")
       response = image_model.generate_content([
        "Describe this image in as much detail as possible",
        img
       ])
       return response.text
    except:
        return "Unsupported file type"
from googleapiclient.discovery import build
from config import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CX
import google.generativeai as genai

genai.configure(api_key=GOOGLE_SEARCH_API_KEY)

model = genai.GenerativeModel("gemini-pro")

def search_web(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
        res = (
            service.cse()
            .list(q=query, cx=GOOGLE_SEARCH_CX, num=5)
            .execute()
        )
        results = res.get("items", [])
        if not results:
            return "No search results found"

        summary_prompt = f"""
        Summarize the key points from the following search results, and provide the link to the result:
        {results}
        """
        response = model.generate_content(summary_prompt)
        return response.text
    except Exception as e:

        return f"Error during web search: {e}"

import logging
import os
import uuid

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaDocument
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from db import DatabaseManager
from gemini_utils import chat_with_gemini, analyze_image
from config import TELEGRAM_BOT_TOKEN
from search_utils import search_web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation states
PHONE_NUMBER = 1
SEARCH_QUERY = 2
FILE_ANALYSIS = 3


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username
    db = DatabaseManager()
    if db.register_user(first_name, username, chat_id):
        keyboard = [[KeyboardButton("Share Phone Number", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Welcome! Please share your phone number.", reply_markup=reply_markup
        )
    else:
        update.message.reply_text("Welcome back!")

def handle_contact(update: Update, context: CallbackContext):
    phone_number = update.message.contact.phone_number
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    db.update_user_phone(chat_id, phone_number)
    update.message.reply_text("Thank you, your phone number has been saved.")

def chat_handler(update: Update, context: CallbackContext):
    user_input = update.message.text
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    response = chat_with_gemini(user_input)
    db.save_chat_history(chat_id, "user", user_input)
    db.save_chat_history(chat_id, "bot", response)
    update.message.reply_text(response)


def start_web_search(update: Update, context: CallbackContext):
    update.message.reply_text("Enter your search query:")
    return SEARCH_QUERY

def handle_web_search(update: Update, context: CallbackContext):
    query = update.message.text
    response = search_web(query)
    update.message.reply_text(response)
    return ConversationHandler.END

def file_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = DatabaseManager()
    file = None
    file_id = None
    file_name = None
    if update.message.photo:
        file = update.message.photo[-1]
        file_id = file.file_id
        file_name = f"{uuid.uuid4().hex}.jpg"
    elif update.message.document:
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name

    if file:
        file_obj = context.bot.get_file(file_id)
        file_path = os.path.join("files",file_name)
        os.makedirs("files",exist_ok=True)
        file_obj.download(file_path)
        analysis = analyze_image(file_path)
        db.save_file_metadata(chat_id, file_name, analysis)
        update.message.reply_text(analysis)
        return ConversationHandler.END
    else:
        update.message.reply_text("Unsupported file type")


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_contact))

    # Web search conversation handler
    web_search_handler = ConversationHandler(
        entry_points=[CommandHandler("websearch", start_web_search)],
        states={
            SEARCH_QUERY: [MessageHandler(Filters.text & ~Filters.command, handle_web_search)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(web_search_handler)

    #File analysis conversation handler
    file_analysis_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo | Filters.document, file_handler)],
        states={},
        fallbacks=[]
    )
    dispatcher.add_handler(file_analysis_handler)

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

























