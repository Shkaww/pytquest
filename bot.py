# bot.py
import os
import json
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
)
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext.filters import TEXT
from queue import Queue
import logging

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://127.0.0.1:8000"  # Адрес вашего API

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния разговора
(
    START,
    HANDLE_USERNAME,
    HANDLE_PASSWORD,
    AUTHENTICATED,
) = range(4)


def start(update: Update, context: CallbackContext) -> int:
    """Начало разговора с ботом."""
    update.message.reply_text(
        "Привет! Для начала работы, пожалуйста, авторизуйтесь или зарегистрируйтесь. Для этого напишите /register или /login"
    )
    return START

def register(update: Update, context: CallbackContext) -> int:
     update.message.reply_text("Введите имя пользователя")
     return HANDLE_USERNAME

def handle_username(update: Update, context: CallbackContext) -> int:
    username = update.message.text
    context.user_data["username"] = username
    update.message.reply_text("Введите пароль")
    return HANDLE_PASSWORD

def handle_password(update: Update, context: CallbackContext) -> int:
    password = update.message.text
    username = context.user_data.get('username')
    if not username:
        update.message.reply_text("Ошибка, введите имя пользователя")
        return START
    try:
        response = requests.post(f"{API_URL}/auth/register", json={"username":username, "password":password})
        response.raise_for_status()
        user_data = response.json()
        context.user_data['user_id'] = user_data["user_id"]
        update.message.reply_text(f"Регистрация прошла успешно. Добро пожаловать, {user_data['username']}!")
        return AUTHENTICATED
    except requests.exceptions.RequestException as e:
        update.message.reply_text(f"Ошибка регистрации: {e}")
        return START

def login(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите имя пользователя")
    return HANDLE_USERNAME

def handle_login_username(update: Update, context: CallbackContext) -> int:
    username = update.message.text
    context.user_data["username"] = username
    update.message.reply_text("Введите пароль")
    return HANDLE_PASSWORD

def handle_login_password(update: Update, context: CallbackContext) -> int:
    password = update.message.text
    username = context.user_data.get('username')
    if not username:
        update.message.reply_text("Ошибка, введите имя пользователя")
        return START
    try:
        response = requests.post(f"{API_URL}/auth/login", json={"username":username, "password":password})
        response.raise_for_status()
        user_data = response.json()
        context.user_data['user_id'] = user_data["user_id"]
        update.message.reply_text(f"Авторизация прошла успешно. Добро пожаловать, {user_data['username']}!")
        return AUTHENTICATED
    except requests.exceptions.RequestException as e:
        update.message.reply_text(f"Ошибка авторизации: {e}")
        return START

def authenticated(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Вы авторизованы")
    return AUTHENTICATED

def main():
    """Запуск бота."""
    update_queue = Queue()
    updater = Updater(TELEGRAM_BOT_TOKEN, update_queue=update_queue)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [
                 CommandHandler('register', register),
                 CommandHandler('login', login),
            ],
            HANDLE_USERNAME: [
                MessageHandler(filters.text, handle_username)
            ],
            HANDLE_PASSWORD: [
                MessageHandler(filters.text, handle_password),
                 MessageHandler(filters.text, handle_login_password)
            ],
            AUTHENTICATED: [
                 MessageHandler(filters.text, authenticated)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling(
        allowed_updates=[Update.MESSAGE]
    )
    updater.idle()


if __name__ == '__main__':
    main()