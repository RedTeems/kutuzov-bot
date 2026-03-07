import logging
import os
import sys
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен из переменной окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    logging.error("❌ TELEGRAM_TOKEN not set")
    sys.exit(1)

# URL вашего бота на Render (замените, если нужно)
RENDER_URL = os.environ.get('RENDER_URL', 'https://kutuzov-bot.onrender.com')
GAME_URL = 'https://kutuzovgames.gusevandrey726.workers.dev'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверка наличия изображений
INTRO_PHOTO = 'KutuzovIntro.jpg'
POD_PHOTO = 'KutuzovPODIntro.jpg'
if not os.path.isfile(INTRO_PHOTO):
    logger.warning(f"⚠️ File {INTRO_PHOTO} not found. Will send text only.")
if not os.path.isfile(POD_PHOTO):
    logger.warning(f"⚠️ File {POD_PHOTO} not found. Will send text only.")

# --- Обработчики команд ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if os.path.isfile(INTRO_PHOTO):
            with open(INTRO_PHOTO, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=(
                        '🎮 Добро пожаловать в игру!\n\n'
                        '🎮 *Kutuzov Game* 🎮\n\n'
                        '🌐 _Советуем включить VPN для захода в игру._\n'
                        '🍀 *Удачи !!!*'
                    ),
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                '🎮 Добро пожаловать в игру!\n\n'
                '🎮 *Kutuzov Game* 🎮\n\n'
                '🌐 _Советуем включить VPN для захода в игру._\n'
                '🍀 *Удачи !!!*',
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
    
    keyboard = [['🎮 ИГРАТЬ']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == '🎮 ИГРАТЬ':
        await update.message.reply_text('🎮', reply_markup=ReplyKeyboardRemove())
        try:
            if os.path.isfile(POD_PHOTO):
                with open(POD_PHOTO, 'rb') as photo:
                    inline_keyboard = [[InlineKeyboardButton('🎮 ИГРАТЬ', url=GAME_URL)]]
                    reply_markup = InlineKeyboardMarkup(inline_keyboard)
                    await update.message.reply_photo(photo=photo, reply_markup=reply_markup)
            else:
                inline_keyboard = [[InlineKeyboardButton('🎮 ИГРАТЬ', url=GAME_URL)]]
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                await update.message.reply_text('Нажмите кнопку ниже:', reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            await update.message.reply_text("Произошла ошибка.")
    else:
        await update.message.reply_text('Пожалуйста, используйте кнопку "🎮 ИГРАТЬ".')

# --- Flask приложение для вебхука ---
app = Flask(__name__)

# Создаём экземпляр Application (один раз)
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Принимает обновления от Telegram."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
        return 'ok'
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'error', 500

@app.route('/')
def index():
    return "✅ Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Устанавливаем вебхук при старте
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")
    
    # Запускаем Flask (без polling)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
