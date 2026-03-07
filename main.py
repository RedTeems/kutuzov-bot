import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота (получите у @BotFather)
TOKEN = '8724824547:AAGyvVyxedJk4YV2hD087A1eqfgh8M_4loA'

# URL игры
GAME_URL = 'https://kutuzovgames.gusevandrey726.workers.dev'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное фото с текстом и эмодзи джойстика с клавиатурой."""
    with open('KutuzovIntro.jpg', 'rb') as photo:
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
    # Клавиатура над полем ввода
    keyboard = [['🎮 ИГРАТЬ']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text('🎮', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатие на reply-кнопку 'ИГРАТЬ'."""
    if update.message.text == '🎮 ИГРАТЬ':
        # Убираем reply-клавиатуру, отправляя эмодзи
        await update.message.reply_text('🎮', reply_markup=ReplyKeyboardRemove())
        # Отправляем второе фото с inline-кнопкой
        with open('KutuzovPODIntro.jpg', 'rb') as photo:
            inline_keyboard = [[InlineKeyboardButton('🎮 ИГРАТЬ', url=GAME_URL)]]
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            await update.message.reply_photo(photo=photo, reply_markup=reply_markup)
    else:
        # Если пользователь написал что-то другое
        await update.message.reply_text('Пожалуйста, используйте кнопку "🎮 ИГРАТЬ".')

def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()