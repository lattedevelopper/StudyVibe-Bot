import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

# Замените на ваш токен от BotFather
TOKEN = "8490585937:AAGa8Po7KC4v6vhaQHSJficyrL8mPjhorQk"

async def start(update: Update, context):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я простой бот. Напиши /start чтобы поздороваться!")

def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик команды /start
    app.add_handler(CommandHandler("start", start))
    
    print("Бот запущен и ожидает сообщения...")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
