import os
from telegram import Update
from telegram.ext import Application, CommandHandler

# Получаем токен из переменных окружения Railway
TOKEN = os.environ.get('8490585937:AAGa8Po7KC4v6vhaQHSJficyrL8mPjhorQk')

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я работаю на Railway 24/7!")

def main():
    if not TOKEN:
        print("Ошибка: BOT_TOKEN не найден!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Бот запущен на Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
