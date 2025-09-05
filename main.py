import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Замените на ваш токен
TOKEN = "8490585937:AAGa8Po7KC4v6vhaQHSJficyrL8mPjhorQk"

async def start(update: Update, context):
    """Обработчик команды /start"""
    # Текст сообщения
    message_text = "👋 Привет! Добро пожаловать в Study Vibe! 📚 Я твой персональный помощник с домашними заданиями. Нажми кнопку - Open, чтобы открыть Study Vibe."
    
    # Отправляем сообщение с кнопкой
    await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup
    )

def main():
    if not TOKEN:
        print("Ошибка: BOT_TOKEN не найден!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    
    print("Study Vibe бот запущен на Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
