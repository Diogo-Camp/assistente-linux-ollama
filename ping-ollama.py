import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Configurações
TOKEN = "8071695340:AAHYqzkjlajRh9xbnbQqxYkFLXDvTk96fCg"  # Substitua pelo seu token do BotFather
OLLAMA_API_URL = "http://192.168.0.36:11434/api/generate"  # URL padrão do Ollama
MODEL_NAME = "mistral"  # Altere se estiver usando outro modelo

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    await update.message.reply_text(
        "Olá! Eu sou um bot integrado com o Mistral via Ollama.\n"
        "Envie /msg seguido da sua pergunta ou mensagem.\n"
        "Exemplo: /msg Explique a teoria da relatividade"
    )

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /msg"""
    # Verifica se há texto após o comando
    if not context.args:
        await update.message.reply_text("Por favor, inclua sua mensagem após o /msg")
        return
    
    user_input = " ".join(context.args)
    await update.message.reply_text("🔍 Processando sua solicitação...")
    
    try:
        # Faz a requisição para a API do Ollama
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": user_input,
                "stream": False
            },
            timeout=60  # Timeout de 60 segundos
        )
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "Não recebi uma resposta válida.")
            
            # Divide a resposta em partes se for muito longa para o Telegram
            if len(answer) > 4000:
                for i in range(0, len(answer), 4000):
                    await update.message.reply_text(answer[i:i+4000])
            else:
                await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f"❌ Erro na API: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        await update.message.reply_text("⚠️ Ocorreu um erro ao acessar a API local. Verifique se o Ollama está rodando.")

def main():
    """Inicializa o bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("msg", handle_msg))
    
    # Mensagem de ajuda para quem enviar texto sem comando
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
        lambda update, ctx: update.message.reply_text("Use /msg seguido da sua pergunta")))
    
    # Inicia o bot
    application.run_polling()
    logger.info("Bot iniciado e pronto para receber mensagens")

if __name__ == "__main__":
    main()
