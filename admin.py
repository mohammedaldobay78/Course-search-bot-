# admin.py
from telebot import TeleBot
from config import BOT_TOKEN, ADMIN_ID
from logs import logger

bot_local = TeleBot(BOT_TOKEN)

def notify_admin(text):
    try:
        if ADMIN_ID and int(ADMIN_ID) != 0:
            bot_local.send_message(ADMIN_ID, text)
            logger.info("Admin notified")
    except Exception as e:
        logger.exception("Failed to notify admin: %s", e)