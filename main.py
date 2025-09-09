import json
import asyncio
import logging
import base64
import io
from typing import List, Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Клиент для работы с DeepSeek через ProxyAPI"""
    
    def __init__(self):
        self.api_key = "sk-kGG3jkmqxnQT2gMYyaMmsMHVNZAvo90x"
        self.base_url = "https://api.proxyapi.ru"
        self.session = None
        
    async def get_session(self):
        """Получить или создать сессию aiohttp"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Закрыть сессию"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def chat(self, messages: List[Dict], max_tokens: int = 3000) -> str:
        """Отправить запрос к DeepSeek API"""
        session = await self.get_session()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        url = f"{self.base_url}/deepseek/chat/completions"
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API Error: {response.status} - {error_text}")
                    return f"Ошибка API: {response.status}"
        except Exception as e:
            logger.error(f"Request error: {e}")
            return f"Ошибка соединения: {str(e)}"

class StudyVibeBot:
    """StudyVibe - школьный помощник на базе ИИ"""
    
    def __init__(self):
        self.telegram_token = "8490585937:AAGZtlnlsHkFTv6HqCCMDTBGkIVLcHMSx88"
        self.deepseek_client = DeepSeekClient()
        self.user_sessions = {}  # Хранение сессий пользователей
        
        # Системный промпт для школьного помощника
        self.system_prompt = """Ты StudyVibe - умный школьный помощник на базе ИИ. Твоя задача - помогать школьникам с учебой.

Что ты умеешь:
- Решать задачи по всем школьным предметам (математика, физика, химия, биология, история, литература, русский и английский язык, география, информатика)
- Объяснять сложные темы простыми словами
- Помогать с домашними заданиями
- Проверять знания и готовить к контрольным
- Анализировать изображения с задачами, формулами, текстами
- Отвечать на любые учебные вопросы

Принципы работы:
- Объясняй пошагово и понятно
- Используй примеры из жизни
- Будь дружелюбным и поддерживающим
- При решении задач показывай весь ход решения
- Если видишь изображение с задачей - анализируй его и помогай решить
- Мотивируй на учебу

Отвечай так, будто ты лучший друг школьника, который всегда готов помочь с учебой!"""
        
    def get_user_session(self, user_id: int) -> List[Dict]:
        """Получить сессию пользователя"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = [{"role": "system", "content": self.system_prompt}]
        return self.user_sessions[user_id]
    
    def add_message_to_session(self, user_id: int, role: str, content: str):
        """Добавить сообщение в сессию пользователя"""
        session = self.get_user_session(user_id)
        session.append({"role": role, "content": content})
        
        # Ограничиваем историю (оставляем системный промпт + 14 сообщений)
        if len(session) > 15:
            system_msg = session[0]  # Системный промпт всегда первый
            recent_messages = session[-14:]
            self.user_sessions[user_id] = [system_msg] + recent_messages
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        welcome_text = f"""
🎓 Привет, {user.first_name}! Я StudyVibe!

Твой умный помощник в учебе! Я помогу с:
📚 Домашними заданиями по всем предметам
🧮 Решением задач и примеров
📖 Объяснением сложных тем
🖼️ Анализом изображений с задачами
✏️ Подготовкой к контрольным и экзаменам

💡 **Как пользоваться:**
• Просто напиши свой вопрос
• Отправь фото с задачей или текстом
• Опиши что тебе нужно объяснить

📋 **Команды:**
/help - Подробная помощь
/clear - Очистить историю чата

Присылай любые учебные вопросы - я всегда готов помочь! 🚀
        """
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать команды"""
        help_text = """
📋 **Команды StudyVibe:**

/start - Главная информация
/help - Список команд  
/clear - Очистить историю чата

Также принимаю текстовые сообщения и изображения.
        """
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить историю диалога"""
        user_id = update.effective_user.id
        # Сбрасываем до изначального состояния с системным промптом
        self.user_sessions[user_id] = [{"role": "system", "content": self.system_prompt}]
        await update.message.reply_text("🗑️ История чата очищена! Начинаем заново! 📚")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик изображений"""
        user = update.effective_user
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Получаем изображение
            photo = update.message.photo[-1]  # Самое большое разрешение
            file = await context.bot.get_file(photo.file_id)
            
            # Загружаем изображение
            image_data = await file.download_as_bytearray()
            
            # Кодируем в base64 для отправки в API
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Получаем подпись к изображению или используем стандартную
            caption = update.message.caption or "Проанализируй это изображение. Если это задача или учебный материал - помоги разобраться и решить."
            
            # Формируем сообщение с изображением
            message_content = f"[ИЗОБРАЖЕНИЕ]: {caption}"
            
            # Добавляем в сессию
            self.add_message_to_session(user.id, "user", message_content)
            
            # Получаем сессию
            session = self.get_user_session(user.id)
            
            # Отправляем запрос к ИИ
            response = await self.deepseek_client.chat(session)
            
            # Добавляем ответ в сессию
            self.add_message_to_session(user.id, "assistant", response)
            
            # Отправляем ответ пользователю
            await update.message.reply_text(
                f"🖼️ **Анализ изображения:**\n\n{response}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing photo: {e}")
            await update.message.reply_text(
                "❌ Не удалось обработать изображение. Попробуй отправить еще раз или опиши задачу текстом."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user = update.effective_user
        
        # Проверка доступа
        if not self.is_user_allowed(user.id):
            await self.access_denied_message(update)
            return
        
        user_message = update.message.text
        
        # Показываем, что бот печатает
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Добавляем сообщение пользователя в сессию
        self.add_message_to_session(user.id, "user", user_message)
        
        # Получаем историю диалога
        session = self.get_user_session(user.id)
        
        try:
            # Отправляем запрос к DeepSeek
            ai_response = await self.deepseek_client.chat(session)
            
            # Добавляем ответ ИИ в сессию
            self.add_message_to_session(user.id, "assistant", ai_response)
            
            # Отправляем ответ пользователю
            response_text = f"🎓 **StudyVibe:**\n\n{ai_response}"
            
            # Если ответ слишком длинный, разбиваем на части
            if len(response_text) > 4000:
                parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode="Markdown")
            else:
                await update.message.reply_text(response_text, parse_mode="Markdown")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                f"❌ Произошла ошибка при обработке запроса. Попробуй еще раз! 🤖"
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Упс! Что-то пошло не так. Попробуй еще раз! 🤖"
            )
    
    def run(self):
        """Запустить бота"""
        app = Application.builder().token(self.telegram_token).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("clear", self.clear_command))
        app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        app.add_error_handler(self.error_handler)
        
        logger.info("StudyVibe бот запущен! 🎓")
        
        # Запускаем бота
        try:
            app.run_polling()
        finally:
            # Закрываем сессию при завершении
            asyncio.run(self.deepseek_client.close_session())

def main():
    """Главная функция"""
    # Создаем и запускаем StudyVibe бота
    bot = StudyVibeBot()
    bot.run()

if __name__ == "__main__":
    main()
