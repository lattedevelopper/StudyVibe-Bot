import os
from telegram import Update
from telegram.ext import Application, CommandHandler

# ЗАМЕНИТЕ НА НОВЫЙ ТОКЕН!
TOKEN = "8490585937:AAGZtlnlsHkFTv6HqCCMDTBGkIVLcHMSx88"

async def start(update: Update, context):
    """Обработчик команды /start"""
    # Многострочное сообщение
    message_text = (
        "👋 Привет! Добро пожаловать в Study Vibe! 📚\n\n"
        "Я твой персональный помощник с домашними заданиями.\n\n"
        "Нажми кнопку - Open, чтобы открыть Study Vibe."
    )
    
    await update.message.reply_text(message_text)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Study Vibe бот запущен...")
    app.run_polling(drop_pending_updates=True)  # Добавил drop_pending_updates

if __name__ == "__main__":
    main()
