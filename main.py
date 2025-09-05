import os
from telegram import Update
from telegram.ext import Application, CommandHandler

# Ваш токен
TOKEN = "8490585937:AAGa8Po7KC4v6vhaQHSJficyrL8mPjhorQk"

async def start(update: Update, context):
    """Обработчик команды /start"""
    message_text = "👋 Привет! Добро пожаловать в Study Vibe! 📚 Я твой персональный помощник с домашними заданиями. Нажми кнопку - Open, чтобы открыть Study Vibe."
    
    await update.message.reply_text(message_text)

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик команды /start
    app.add_handler(CommandHandler("start", start))
    
    print("Study Vibe бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
