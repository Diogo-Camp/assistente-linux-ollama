import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Configuração
TOKEN = "8071695340:AAHYqzkjlajRh9xbnbQqxYkFLXDvTk96fCg"  # ← Substitua pelo seu token real
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start"""
    keyboard = [
        [InlineKeyboardButton("🛒 Comprar por R$10,00", callback_data='buy_10')],
        [InlineKeyboardButton("📅 Assinatura Mensal R$20,00", callback_data='sub_20')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Olá {update.effective_user.first_name}! Escolha uma opção:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para os botões inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'buy_10':
        await query.edit_message_text(
            "✅ Compra única de R$10,00\n\n"
            "🔗 Link: https://seusite.com/10reais"
        )
    elif query.data == 'sub_20':
        await query.edit_message_text(
            "✅ Assinatura mensal de R$20,00\n\n"
            "🔗 Link: https://seusite.com/20reais\n\n"
            "🔄 Renovação automática mensal"
        )

def main() -> None:
    """Função principal"""
    # Cria a aplicação
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Adiciona os handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Inicia o bot
    application.run_polling()

if __name__ == '__main__':
    main()